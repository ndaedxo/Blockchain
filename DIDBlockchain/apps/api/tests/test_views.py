from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.blockchain import  DIDDocument
from apps.blockchain.transaction import Transaction
from apps.blockchain.validator import  Validator
from apps.blockchain.blockchain import Blockchain  # Your custom blockchain class
from ..serializers.DIDDocumentServiceSerializer import TransactionSerializer, ValidatorSerializer, DIDDocumentSerializer


class CustomUserTestCase(APITestCase):
    def setUp(self):
        
        self.client.login(username='ndae', password='Douvretenser30')  # Log in the user for authenticated tests

    def test_create_transaction(self):
        """Test creating a transaction."""
        url = reverse('transaction-list')  # Adjust with your actual URL name
        data = {
            'recipient': '0d44df41faebb0c4fd79c71fcfb0b250a163d441ca',
            'amount': 0.0,
            'signature': 'signature_example'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Transaction.objects.filter(sender=self.user.username).exists())

    def test_list_blocks(self):
        """Test listing all blocks."""
        url = reverse('block-list')  # Adjust with your actual URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_block(self):
        """Test retrieving a specific block."""
        url = reverse('block-detail', kwargs={'pk': 0})  # Adjust with your actual URL name
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_validator(self):
        """Test creating a validator."""
        url = reverse('validator-list')  # Adjust with your actual URL name
        data = {
            'stake': 1000.0,
            'public_key': self.user.public_key
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Validator.objects.filter(address=self.user.username).exists())

    def test_did_document_creation(self):
        """Test creating a DID Document."""
        url = reverse('did-document-list')  # Adjust with your actual URL name
        data = {
            'controller': self.user.username,
            'public_key': self.user.public_key,
            'authentication': [],
            'service_endpoints': [],
            'status': 'active'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(DIDDocument.objects.filter(controller=self.user.username).exists())
