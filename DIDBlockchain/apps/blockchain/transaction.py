# DIDBlockchain/apps/blockchain/transaction.py

from django.db import models
from .logic.transaction_logic import TransactionLogic

class Transaction(models.Model):
    sender = models.CharField(max_length=255)
    recipient = models.JSONField()
    timestamp = models.FloatField()
    fee = models.FloatField(default=0.0)
    signature = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return f"{self.sender} -> {self.recipient} at {self.timestamp}"

    def to_logic(self) -> TransactionLogic:
        """Convert the Django model instance to a TransactionLogic instance."""
        return TransactionLogic(
            sender=self.sender,
            recipient=self.recipient,
            timestamp=self.timestamp,
            fee=self.fee,
            signature=self.signature.hex() if self.signature else None
        )
