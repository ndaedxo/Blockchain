# DIDBlockchain\apps\blockchain\blockchain.py
import hashlib
import json
from time import time
import logging
from typing import List, Dict, Any, Optional
from .block import Block
from .transaction import Transaction
from .validator import Validator
from .exceptions import InvalidBlockError, InvalidTransactionError
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

logger = logging.getLogger(__name__)

class Blockchain:
    def __init__(self):
        """Initialize the blockchain with a genesis block."""
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.validators: List[Validator] = []

        # Create the first block in the chain (genesis block)
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time(),
            previous_hash="0" * 64,
            validator="genesis"
        )
        genesis_block.finalize_block()
        self.chain.append(genesis_block)

    def add_block(self, block: Block, validator_signature: str) -> bool:
        """Add a new block after verification."""
        previous_block = self.get_last_block()
        try:
            if not self._verify_block(block, previous_block, validator_signature):
                raise InvalidBlockError("Block verification failed.")
            
            block.finalize_block()
            self.chain.append(block)

            # Clear pending transactions
            self.pending_transactions = [
                tx for tx in self.pending_transactions if tx not in block.transactions
            ]
            logger.info(f"Block {block.index} added by {block.validator}.")
            return True
        except InvalidBlockError as e:
            logger.error(f"Failed to add block: {e}")
            return False

    def _verify_block(self, block: Block, previous_block: Block, validator_signature: str) -> bool:
        logger.debug(f"Verifying block: {block.index} against previous block: {previous_block.index}")

        # Check index
        if previous_block.index + 1 != block.index:
            logger.error(f"Index mismatch. Previous: {previous_block.index}, Current: {block.index}")
            raise InvalidBlockError("Index Mismatch: Current block index does not follow the previous.")
        
        # Check previous hash
        if block.previous_hash != previous_block.hash:
            logger.error(f"Previous hash mismatch. Expected: {previous_block.hash}, Found: {block.previous_hash}")
            raise InvalidBlockError(f"Previous Hash Mismatch: Expected {previous_block.hash}, but got {block.previous_hash}.")

        # Verify validator signature
        if not self._verify_validator_signature(block, validator_signature):
            logger.error("Validator signature verification failed.")
            raise InvalidBlockError("Validator Signature Issue: Signature verification failed.")
        
        logger.info("Block verified successfully.")
        return True

    def _verify_proof(self, block: Block, proof: str) -> bool:
        """Verify a basic proof-of-work for demonstration."""
        guess = f"{block.index}{block.previous_hash}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def _verify_validator_signature(self, block: Block, signature: str) -> bool:
        """Verifies validator's signature."""
        validator = next((v for v in self.validators if v.address == block.validator), None)
        if not validator:
            logger.error("Validator not found.")
            raise InvalidBlockError("Validator Signature Issue: Validator not found.")

        try:
            public_key = load_pem_public_key(validator.public_key_pem)
            public_key.verify(
                signature,
                block.hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            raise InvalidBlockError("Validator Signature Issue: Signature verification failed.")

    def get_last_block(self) -> Block:
        """Get the last block in the chain."""
        return self.chain[-1]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the blockchain to dictionary."""
        return {
            'chain': [block.to_dict() for block in self.chain],
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'validators': [validator.to_dict() for validator in self.validators]
        }
    
    def get_all_transactions(self) -> List[Transaction]:
        """Retrieve all transactions in chain."""
        all_transactions = [tx for block in self.chain for tx in block.transactions]
        all_transactions.extend(self.pending_transactions)
        return all_transactions
    
    def add_pending_transaction(self, transaction):
        """Add a transaction to the pending transactions pool."""
        self.pending_transactions.append(transaction)

    def has_pending_transactions(self):
        """Check if there are any pending transactions."""
        return bool(self.pending_transactions)

    def add_transaction_to_block(self, transaction):
        """Add a transaction to the next block (this is a simplified example)."""
        self.pending_transactions.remove(transaction)
