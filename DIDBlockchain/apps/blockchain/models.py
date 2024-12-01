# DIDBlockchain\apps\blockchain\models.py
from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
import json
import uuid
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

def default_empty_list():
    return []

def default_empty_dict():
    return {}

class DIDDocument(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('DEACTIVATED', 'Deactivated'),
        ('REVOKED', 'Revoked'),
    ]

    did = models.CharField(max_length=100, unique=True, primary_key=True)
    controller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='controlled_dids')
    version = models.PositiveIntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    public_key = models.TextField()
    
    service_endpoints = models.JSONField(default=default_empty_list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    proof = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=default_empty_dict)
    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return f"DID: {self.did} (Version {self.version})"

    def clean(self):
        if not self.did.startswith('did:'):
            raise ValidationError({'did': 'DID must start with "did:"'})
        if not self._is_valid_public_key(self.public_key):
            raise ValidationError({'public_key': 'Invalid public key format'})
        super().clean()

    def save(self, *args, **kwargs):
        if not self.did:
            self.did = f"did:example:{uuid.uuid4().hex}"
        if self.pk:
            self.version += 1
        self.full_clean()
        super().save(*args, **kwargs)

    def _is_valid_public_key(self, public_key):
        # Example placeholder; replace with real validation
        return len(public_key) > 30

    def to_dict(self):
        return {
            "@context": ["https://www.w3.org/ns/did/v1", "https://w3id.org/security/v1"],
            "id": self.did,
            "controller": self.controller.username,
            "verificationMethod": [{
                "id": f"{self.did}#keys-1",
                "type": "Ed25519VerificationKey2020",
                "controller": self.did,
                "publicKeyBase58": self.public_key
            }],
            "authentication": self.authentication,
            "service": self.service_endpoints,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "proof": self.proof,
            "version": self.version
        }

    def deactivate(self):
        self.status = 'DEACTIVATED'
        self.save()

    def revoke(self):
        self.status = 'REVOKED'
        self.save()

    def add_service_endpoint(self, type_name, endpoint):
        if not endpoint.startswith('https://'):
            raise ValidationError({'service_endpoints': 'Service endpoint must be a valid HTTPS URL'})
        service = {
            "id": f"{self.did}#service-{len(self.service_endpoints) + 1}",
            "type": type_name,
            "serviceEndpoint": endpoint
        }
        self.service_endpoints.append(service)
        self.save()


    def add_authentication_method(self, method):
        auth = {
            "id": f"{self.did}#authn-{len(self.authentication) + 1}",
            "type": method["type"],
            "controller": self.did,
            **method
        }
        self.authentication.append(auth)
        self.save()

    def update_proof(self, proof_type, proof_value, creator):
        self.proof = {
            "type": proof_type,
            "created": datetime.utcnow().isoformat(),
            "creator": creator,
            "proofValue": proof_value
        }
        self.save()


class DIDResolutionMetadata(models.Model):
    did = models.ForeignKey(DIDDocument, on_delete=models.CASCADE, related_name='resolution_metadata')
    resolver = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']


class DIDTransaction(models.Model):
    OPERATION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DEACTIVATE', 'Deactivate'),
        ('REVOKE', 'Revoke')
    ]

    did_document = models.ForeignKey(DIDDocument, on_delete=models.CASCADE, related_name='transactions')
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    previous_state = models.JSONField(null=True, blank=True)
    new_state = models.JSONField()
    transaction_hash = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ['-timestamp']

# DIDBlockchain\apps\blockchain\models.py
from django.db import models

class Validator(models.Model):
    address = models.CharField(max_length=100, unique=True)
    stake = models.DecimalField(max_digits=20, decimal_places=8)
    public_key = models.TextField()
    private_key = models.TextField(blank=True, null=True)  # Add this line to store private key PEM
    reputation_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    last_block_validated = models.DateTimeField(null=True, blank=True)
    rewards = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    blocks_validated = models.IntegerField(default=0)
    is_slashed = models.BooleanField(default=False)
    validation_failures = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    stake = models.DecimalField(max_digits=20, decimal_places=8)

    def has_sufficient_stake(self, minimum_stake):
        return self.stake >= minimum_stake
    
    def __str__(self):
        return f"Validator {self.address}"
