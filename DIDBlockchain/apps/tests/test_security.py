import unittest
from blockchain.security import SecurityManager
import json

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.security_manager = SecurityManager()
        self.private_key, self.public_key = self.security_manager.generate_key_pair()

    def test_key_generation(self):
        """Test key pair generation"""
        private_key, public_key = self.security_manager.generate_key_pair()
        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)

    def test_hash_calculation(self):
        """Test hash calculation"""
        data = {"test": "data"}
        hash1 = self.security_manager.calculate_hash(data)
        hash2 = self.security_manager.calculate_hash(data)
        self.assertEqual(hash1, hash2)
        
        # Test different data produces different hashes
        data2 = {"test": "different"}
        hash3 = self.security_manager.calculate_hash(data2)
        self.assertNotEqual(hash1, hash3)

    def test_signature_verification(self):
        """Test digital signature creation and verification"""
        data = {"message": "test"}
        signature = self.security_manager.sign_data(self.private_key, data)
        
        # Verify valid signature
        self.assertTrue(
            self.security_manager.verify_signature(
                self.public_key,
                signature,
                data
            )
        )
        
        # Verify tampered data fails
        tampered_data = {"message": "tampered"}
        self.assertFalse(
            self.security_manager.verify_signature(
                self.public_key,
                signature,
                tampered_data
            )
        )

    def test_merkle_root(self):
        """Test Merkle root calculation"""
        transactions = [
            {"id": 1, "data": "test1"},
            {"id": 2, "data": "test2"},
            {"id": 3, "data": "test3"}
        ]
        
        root1 = self.security_manager.merkle_root(transactions)
        self.assertIsNotNone(root1)
        
        # Test same transactions produce same root
        root2 = self.security_manager.merkle_root(transactions)
        self.assertEqual(root1, root2)
        
        # Test different transactions produce different root
        transactions.append({"id": 4, "data": "test4"})
        root3 = self.security_manager.merkle_root(transactions)
        self.assertNotEqual(root1, root3)

if __name__ == '__main__':
    unittest.main()