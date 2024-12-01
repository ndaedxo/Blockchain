# tests/test_blockchain.py
import unittest
from unittest.mock import Mock, patch
from blockchain.blockchain import Blockchain
from blockchain.block import Block
from blockchain.transaction import Transaction
from blockchain.validator import Validator
from cryptography.hazmat.primitives.asymmetric import rsa
import time

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.blockchain = Blockchain()
        
        # Create test private/public key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
        
        # Create test validator
        self.validator = Validator(
            address="test_validator",
            stake=1000.0,
            public_key=self.public_key
        )
        self.blockchain.validators.append(self.validator)

    def test_create_genesis_block(self):
        """Test genesis block creation"""
        self.assertEqual(len(self.blockchain.chain), 1)
        genesis_block = self.blockchain.chain[0]
        self.assertEqual(genesis_block.index, 0)
        self.assertEqual(genesis_block.previous_hash, "0" * 64)
        self.assertEqual(len(genesis_block.transactions), 0)

    def test_add_transaction(self):
        """Test adding a transaction to the blockchain"""
        transaction = Transaction(
            sender="test_sender",
            identity_data={"name": "Test User", "id": "123"},
            timestamp=time.time()
        )
        transaction.sign_transaction(self.private_key)
        
        block_index = self.blockchain.add_transaction(transaction)
        self.assertEqual(block_index, 1)
        self.assertEqual(len(self.blockchain.pending_transactions), 1)

    def test_add_block(self):
        """Test adding a new block to the chain"""
        # Create and add a transaction
        transaction = Transaction(
            sender="test_sender",
            identity_data={"name": "Test User", "id": "123"},
            timestamp=time.time()
        )
        transaction.sign_transaction(self.private_key)
        self.blockchain.add_transaction(transaction)

        # Create and add block
        previous_block = self.blockchain.get_last_block()
        new_block = Block(
            index=previous_block.index + 1,
            transactions=self.blockchain.pending_transactions,
            timestamp=time.time(),
            previous_hash=previous_block.calculate_hash(),
            validator=self.validator.address
        )
        
        # Sign block
        proof = "test_proof"
        signature = self.validator.sign_block(new_block)
        
        # Add block to chain
        result = self.blockchain.add_block(new_block, proof, signature)
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(len(self.blockchain.pending_transactions), 0)

    def test_verify_chain(self):
        """Test blockchain verification"""
        # Add a few blocks
        for i in range(3):
            transaction = Transaction(
                sender=f"sender_{i}",
                identity_data={"name": f"User {i}", "id": str(i)},
                timestamp=time.time()
            )
            transaction.sign_transaction(self.private_key)
            self.blockchain.add_transaction(transaction)
            
            previous_block = self.blockchain.get_last_block()
            new_block = Block(
                index=previous_block.index + 1,
                transactions=self.blockchain.pending_transactions,
                timestamp=time.time(),
                previous_hash=previous_block.calculate_hash(),
                validator=self.validator.address
            )
            
            proof = f"test_proof_{i}"
            signature = self.validator.sign_block(new_block)
            self.blockchain.add_block(new_block, proof, signature)

        # Verify chain
        self.assertTrue(self.blockchain.verify_chain())

        # Tamper with a block
        self.blockchain.chain[1].transactions[0].identity_data["name"] = "Tampered"
        self.assertFalse(self.blockchain.verify_chain())

    def test_consensus_mechanism(self):
        """Test the consensus mechanism"""
        # Add multiple validators
        validator2 = Validator(
            address="validator2",
            stake=2000.0,
            public_key=rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            ).public_key()
        )
        self.blockchain.validators.append(validator2)

        # Verify validator selection is weighted by stake
        selections = {v.address: 0 for v in self.blockchain.validators}
        for _ in range(1000):
            selected = self.blockchain.consensus.select_validator(int(time.time()))
            selections[selected.address] += 1

        # validator2 should be selected more often due to higher stake
        self.assertGreater(
            selections["validator2"],
            selections["test_validator"]
        )

    def test_validator_rewards(self):
        """Test validator reward distribution"""
        initial_rewards = self.validator.rewards
        
        # Create and add a block
        transaction = Transaction(
            sender="test_sender",
            identity_data={"name": "Test User", "id": "123"},
            timestamp=time.time()
        )
        transaction.sign_transaction(self.private_key)
        self.blockchain.add_transaction(transaction)

        previous_block = self.blockchain.get_last_block()
        new_block = Block(
            index=previous_block.index + 1,
            transactions=self.blockchain.pending_transactions,
            timestamp=time.time(),
            previous_hash=previous_block.calculate_hash(),
            validator=self.validator.address
        )
        
        proof = "test_proof"
        signature = self.validator.sign_block(new_block)
        self.blockchain.add_block(new_block, proof, signature)

        # Verify rewards were distributed
        self.assertGreater(self.validator.rewards, initial_rewards)

if __name__ == '__main__':
    unittest.main()