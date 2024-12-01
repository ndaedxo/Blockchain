# DIDBlockchain\apps\users\models.py
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from apps.wallet.models import Wallet  # Import the Wallet model
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save
import binascii
import os
import hashlib
from apps.api.secure_storage import SecureStorage  # Import SecureStorage
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)

        private_key = self.generate_private_key()
        public_key = private_key.public_key()  # Keep public_key as an object
        wallet_address = self.generate_wallet_address(public_key)

        # Set the private key, public key, and wallet address
        user.private_key = private_key  # Store as is for secure storage
        user.public_key = public_key.public_bytes(  # Serialize for storage
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')  # Store as a string in the database

        user.wallet_address = wallet_address
        # Generate DID
        user.did = self.generate_did(public_key)  # Call to generate DID
        
        user.save(using=self._db)

        # Store the private key securely
        secure_storage = SecureStorage()
        secure_storage.store_private_key(username, private_key)

        # Check if a wallet already exists for the user
        if not Wallet.objects.filter(user=user).exists():
            Wallet.objects.create(user=user, wallet_address=user.wallet_address)

        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(username, email, password, **extra_fields)

        # Generate the public key from the private key
        private_key = self.generate_private_key()
        public_key = private_key.public_key()  # Keep public_key as an object
        wallet_address = self.generate_wallet_address(public_key)

        user.private_key = private_key  # Store as is for secure storage
        user.public_key = public_key.public_bytes(  # Serialize for storage
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')  # Store as a string in the database

        user.wallet_address = wallet_address
        # Generate DID
        user.did = self.generate_did(public_key)  # Call to generate DID
        
        user.save(using=self._db)

        # Store the private key securely
        secure_storage = SecureStorage()
        secure_storage.store_private_key(username, private_key)

        # Check if a wallet already exists for the user
        if not Wallet.objects.filter(user=user).exists():
            Wallet.objects.create(user=user, wallet_address=user.wallet_address)

        return user
    
    def generate_private_key(self):
        # Generate an RSA private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        return private_key

    def generate_wallet_address(self, public_key):
        # Serialize the public key to bytes and create a wallet address
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return hashlib.sha256(public_key_bytes).hexdigest()[:42]
    def generate_public_key(self, private_key):
        # Serialize the private key to PEM format
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        return hashlib.sha256(pem).hexdigest()
    # Method to generate a DID using the public key
    def generate_did(self, public_key):
        # Serialize the public key to bytes
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Generate the DID using the serialized public key
        did_hash = hashlib.sha256(public_key_bytes).hexdigest()
        did = f"did:mim:{did_hash}"  # Use a specific prefix for your DID

        # Ensure the DID is unique
        while CustomUser.objects.filter(did=did).exists():
            did_hash = hashlib.sha256(os.urandom(32)).hexdigest()  # Regenerate if not unique
            did = f"did:mim:{did_hash}"

        return did


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    
    private_key = EncryptedCharField(max_length=512)  # Increase as necessary
    public_key = models.CharField(max_length=512, blank=True)  # Increase as necessary
    
    wallet_address = models.CharField(max_length=142, blank=True)
   
   # New field for the DID
    did = models.CharField(max_length=255, unique=True, blank=True)  # Add DID field
    
    role = models.CharField(max_length=50, choices=[('user', 'User'), ('validator', 'Validator')], default='user')
    status = models.CharField(max_length=50, default='active')
    
    profile_picture = models.URLField(blank=True, null=True)
    social_media_links = models.JSONField(null=True, blank=True)  # Allow null values
    reputation_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    multi_signature_requirements = models.JSONField(null=True, default=dict, blank=True)
    last_active_timestamp = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)  # Add this field for user activation status
    is_staff = models.BooleanField(default=False)  # Add this field to track staff status
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    multi_signature_requirements = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
# Signal to create a wallet for new users (if it doesn't exist)
@receiver(post_save, sender=CustomUser)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.get_or_create(user=instance, wallet_address=instance.wallet_address)
