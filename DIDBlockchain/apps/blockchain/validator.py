# DIDBlockchain\apps\blockchain\validator.py
from django.db import models
from apps.wallet.models import Wallet  # Import Wallet

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
import time
import logging

logger = logging.getLogger(__name__)


class Validator:
    def __init__(self, address: str, stake: float, public_key: rsa.RSAPublicKey,  private_key: Optional[str] = None):
        self.address = address
        self.stake = stake
        self.public_key = public_key 
        self.rewards = 0.0
        self.last_block_time = 0
        self.blocks_validated = 0
        self.is_slashed = False
        self.validation_failures = 0
        self.joined_at = time.time() # Ensure private key PEM is passed during initialization
        self.private_key = private_key

    def sign(self, data):
        # Ensure 'data' is in bytes
        if isinstance(data, str):
            data = data.encode('utf-8')

        if isinstance(self.private_key, str):
            private_key = serialization.load_pem_private_key(
                self.private_key.encode('utf-8'),  # Encode to bytes
                password=None,
                backend=default_backend()
            )
        else:
            raise ValueError("Private key must be a string")

        signature = private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature

    def sign_block(self, block: Any, minimum_stake: float) -> Optional[bytes]:
        if not self.has_sufficient_stake(minimum_stake):
            raise ValueError("Insufficient stake to validate this block")
        
        if not self.private_key:
            raise ValueError("Private key is required to sign a block")
        
        try:
            block_hash = block.calculate_hash().encode()
            # Convert private key to bytes
            private_key_bytes = self.private_key.encode('utf-8')  # Ensure it's bytes

            private_key = load_pem_private_key(private_key_bytes, password=None)
            
            signature = private_key.sign(
                block_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature
        except (TypeError, ValueError, InvalidSignature) as e:
            logger.error(f"Signing error for validator {self.address}: {e}")
            return None


    def verify_block_signature(self, block: Any, signature: bytes) -> bool:
        """Verify a block's signature."""
        try:
            block_hash = block.calculate_hash().encode()
            self.public_key.verify(
                signature,
                block_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            self.validation_failures += 1
            return False

    def add_stake(self, amount: float) -> bool:
        """Add stake (in DIDcoin) to the validator."""
        if amount <= 0:
            return False
        self.stake += amount
        return True

    def remove_stake(self, amount: float) -> bool:
        """Remove stake (in DIDcoin) from the validator."""
        if amount <= 0 or amount > self.stake:
            return False
        self.stake -= amount
        return True
    
    def has_sufficient_stake(self, minimum_stake: float) -> bool:
        """Check if the validator's stake meets the minimum required stake."""
        return self.stake >= minimum_stake

        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validator to a dictionary."""
        return {
            'address': self.address,
            'stake': self.stake,
            'rewards': self.rewards,
            'blocks_validated': self.blocks_validated,
            'is_slashed': self.is_slashed,
            'validation_failures': self.validation_failures,
            'joined_at': self.joined_at
        }
