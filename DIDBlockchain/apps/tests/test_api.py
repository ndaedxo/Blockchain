# tests/test_api.py
import unittest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
import json
import time

class BlockchainAPITest(TestCase):
    def setUp(self):
        """Set up test environment"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.blockchain = Blockchain()

    def test_get_blockchain(self):
        """Test retrieving the blockchain"""
        response = self.client.get(reverse('blockchain-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))
        # Should have at least genesis block
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_block(self):
        """Test retrieving a specific block"""
        response = self.client.get(
            reverse('blockchain-detail', kwargs={'pk': 0})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['index'], 0)  # Genesis block

    def test_get_pending_transactions(self):
        """Test retrieving pending transactions"""
        response = self.client.get(
            reverse('blockchain-pending-transactions')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

    def test_create_transaction(self):
        """Test creating a new transaction"""
        transaction_data = {
            'identity_data': {
                'name': 'Test User',
                'id': '123456789'
            }
        }
        response = self.client.post(
            reverse('transaction-list'),
            data=json.dumps(transaction_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('block_index', response.data)

    def test_register_validator(self):
        """Test validator registration"""
        validator_data = {
            'stake': 1000.0,
            'public_key': 'test_public_key'
        }
        response = self.client.post(
            reverse('validator-list'),
            data=json.dumps(validator_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('validator', response.data)

    def test_chain_status(self):
        """Test retrieving chain status"""
        response = self.client.get(reverse('blockchain-chain-status'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('length', response.data)
        self.assertIn('last_block', response.data)
        self.assertIn('pending_transactions', response.data)

    def test_invalid_transaction(self):
        """Test creating an invalid transaction"""
        invalid_data = {
            'identity_data': None  # Invalid data
        }
        response = self.client.post(
            reverse('transaction-list'),
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse('blockchain-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_validator_insufficient_stake(self):
        """Test validator registration with insufficient stake"""
        validator_data = {
            'stake': 10.0,  # Below minimum stake requirement
            'public_key': 'test_public_key'
        }
        response = self.client.post(
            reverse('validator-list'),
            data=json.dumps(validator_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

if __name__ == '__main__':
    unittest.main()