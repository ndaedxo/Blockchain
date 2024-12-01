# DIDBlockchain\apps\blockchain\consensus.py
from typing import List, Optional
import random
import time
from .validator import Validator
from .block import Block
from .transaction import Transaction

import random
import time

class ProofOfStake:
    def __init__(self, validators: List[Validator]):
        self.validators = validators
        self.minimum_stake = 1000  # Minimum stake in DIDcoin
        self.block_time = 30  # Target time between blocks in seconds

    def select_validator(self, seed: int) -> Optional[Validator]:
        """Selects a validator based on stake and reputation."""
        total_stake = sum(
            v.stake * (1 + v.user.reputation_score / 100) 
            for v in self.validators if v.stake >= self.minimum_stake
        )
        if total_stake == 0:
            return None

        random.seed(seed)
        point = random.uniform(0, total_stake)
        current_pos = 0
        for validator in self.validators:
            weighted_stake = validator.stake * (1 + validator.user.reputation_score / 100)
            current_pos += weighted_stake
            if current_pos > point:
                return validator
        return self.validators[-1]

    def validate_block(self, block: Block, validator: Validator) -> bool:
        """Validate block based on PoS rules."""
        if validator.stake < self.minimum_stake or validator not in self.validators:
            return False
        return (block.timestamp - self.get_last_block_time()) >= self.block_time

    def create_block(self, pending_transactions: List[Transaction], previous_hash: str, validator: Validator) -> Optional[Block]:
        """Creates a new block and signs it."""
        if not self.validate_stake(validator):
            return None

        block = Block(
            index=len(self.get_chain()),
            transactions=pending_transactions[:100],  
            timestamp=time(),
            previous_hash=previous_hash,
            validator=validator.address
        )

        signature = validator.sign_block(block)
        if not signature:
            return None
        block.signature = signature
        return block

    def distribute_rewards(self, block: Block) -> None:
        """Distributes rewards to the validator who created the block."""
        validator = next((v for v in self.validators if v.address == block.validator), None)
        if validator:
            reward = self.calculate_rewards(block)
            validator.add_rewards(reward)

    def slash_validator(self, validator: Validator, reason: str) -> None:
        """Slashes a validator's stake for misbehavior."""
        if validator in self.validators:
            slash_amount = validator.stake * 0.1
            validator.slash_stake(slash_amount)
            
            if validator.stake < self.minimum_stake:
                self.validators.remove(validator)
                print(f"Validator {validator.address} slashed for: {reason}")
