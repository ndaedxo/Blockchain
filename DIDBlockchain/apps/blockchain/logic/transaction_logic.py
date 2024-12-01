# DIDBlockchain/apps/blockchain/logic/transaction_logic.py

import hashlib
import json
from typing import Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

class TransactionLogic:
    def __init__(self, sender: str, recipient: Dict[str, Any], 
                 timestamp: float, fee: float, signature: str = None):
        """Initialize a new Transaction."""
        self.sender = sender
        self.recipient = recipient
        self.timestamp = timestamp
        self.fee = fee  # Transaction fee in DIDcoin
        self.signature = signature  # Signature initialized with provided value
        
    def calculate_hash(self) -> str:
        """Calculate hash of the transaction."""
        transaction_string = json.dumps(self.to_dict(include_signature=False), sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign_transaction(self, private_key: rsa.RSAPrivateKey) -> None:
        """Sign the transaction with the private key."""
        transaction_hash = self.calculate_hash().encode()
        self.signature = private_key.sign(
            transaction_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify_signature(self, public_key: rsa.RSAPublicKey) -> bool:
        """Verify the transaction signature."""
        if not self.signature:
            return False

        try:
            transaction_hash = self.calculate_hash().encode()
            public_key.verify(
                self.signature,
                transaction_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    def to_dict(self, include_signature: bool = True) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        data = {
            'sender': self.sender,
            'recipient': self.recipient,
            'timestamp': self.timestamp,
            'fee': self.fee,
        }
        if include_signature and self.signature:
            data['signature'] = self.signature.hex()
        return data
