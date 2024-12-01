# DIDBlockchain/apps/wallet/models.py
from django.db import models
from django.conf import settings
import hashlib
from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=19, decimal_places=4, default=0.0)
    transaction_history = models.JSONField(default=list)
    wallet_address = models.CharField(max_length=42, unique=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    
    def save(self, *args, **kwargs):
        if not self.wallet_address:
         # Generate a wallet address if it doesn't exist (this can be a hash of the user's public key)
            self.wallet_address = hashlib.sha256(self.user.public_key.encode()).hexdigest()[:42]
        super(Wallet, self).save(*args, **kwargs)

