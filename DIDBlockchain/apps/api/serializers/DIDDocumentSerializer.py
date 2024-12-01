# DIDBlockchain\apps\api\serializers\DIDDocumentSerializer.py
from rest_framework import serializers
from apps.blockchain.models import DIDDocument as DIDDocumentModel
from .DIDDocumentServiceSerializer import DIDDocumentServiceSerializer

class DIDDocumentSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField()

    class Meta:
        model = DIDDocumentModel
        fields = ['controller', 'public_key', 'authentication', 'service_endpoints', 'status', 'created', 'updated', 'version', 'services']
        read_only_fields = ['public_key']

    def get_services(self, obj):
        # Ensure that `obj` is an instance of `DIDDocumentModel`
        if hasattr(obj, 'service_endpoints'):
            return obj.service_endpoints  # Assuming service_endpoints is a field on the model
        return []  # Return an empty list if no service_endpoints found
