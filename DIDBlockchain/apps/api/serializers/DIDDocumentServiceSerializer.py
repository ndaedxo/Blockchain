# DIDBlockchain\apps\api\serializers\DIDDocumentServiceSerializer.py
from rest_framework import serializers
from apps.blockchain.models import DIDDocument as DIDDocumentModel, DIDTransaction

class DIDDocumentServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DIDDocumentModel
        fields = ['controller', 'public_key', 'authentication', 'service_endpoints', 'status', 'created', 'updated', 'version']
        read_only_fields = ['public_key']
        
class DIDTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DIDTransaction
        fields = ['id', 'did_document', 'operation', 'timestamp', 'previous_state', 'new_state', 'transaction_hash']
