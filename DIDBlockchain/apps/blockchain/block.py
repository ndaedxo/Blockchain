# DIDBlockchain\apps\blockchain\block.py
import hashlib
import json
from time import time
from typing import List, Dict, Any
from .transaction import Transaction

class Block:
    def __init__(self, index: int, transactions: List[Transaction], 
                 timestamp: float, previous_hash: str, validator: str, nonce: int = 0):
        """Initialize a new Block."""
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.validator = validator
        self.nonce = nonce
        self.hash = 0  # This will be calculated later
        
    def calculate_hash(self) -> str:
        """Calculate the SHA256 hash of the block."""
        block_string = json.dumps(self.to_dict(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the block to a dictionary."""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'validator': self.validator,
            'nonce': self.nonce,
            'hash': self.hash,
            'previous_hash': self.previous_hash
        }

    def finalize_block(self):
        """Calculate the hash of the block."""
        block_string = json.dumps(self.to_dict(), sort_keys=True).encode()
        self.hash = hashlib.sha256(block_string).hexdigest()