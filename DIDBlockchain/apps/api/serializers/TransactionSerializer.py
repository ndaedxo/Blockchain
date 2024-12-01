#DIDBlockchain\apps\api\serializers\TransactionSerializer.py
from rest_framework import serializers
from apps.blockchain.transaction import Transaction
from django.utils import timezone
from ..secure_storage import SecureStorage
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class TransactionSerializer(serializers.Serializer):
    sender = serializers.CharField(required=False)
    recipient = serializers.JSONField(required=True)
    timestamp = serializers.FloatField(required=False)
    fee = serializers.FloatField(required=False, default=0.0)
    signature = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        validated_data['timestamp'] = validated_data.get('timestamp', timezone.now().timestamp())
        validated_data['fee'] = validated_data.get('fee', 0.0)

        sender_username = self.context['request'].user.username

        if not sender_username:
            raise serializers.ValidationError("Sender username cannot be empty.")

        validated_data['sender'] = sender_username
        # Create a Transaction model instance
        transaction_model_instance = Transaction(**validated_data)
        transaction_model_instance.save()  # Save it to the database first to get an ID

        # Now create a TransactionLogic instance
        transaction_logic_instance = transaction_model_instance.to_logic()

        # Retrieve the private key and sign the transaction
        secure_storage = SecureStorage()
        private_key = secure_storage.retrieve_private_key(sender_username)

        transaction_logic_instance.sign_transaction(private_key)

        # Update the model instance with the signature
        transaction_model_instance.signature = transaction_logic_instance.signature
        transaction_model_instance.save()  # Save the signature back to the database

        return transaction_model_instance

    def to_representation(self, instance):
        return {
            'sender': instance.sender,
            'recipient': instance.recipient,
            'timestamp': instance.timestamp,
            'signature': instance.signature.hex() if instance.signature else None
        }

    

class CreateTransactionSerializer(serializers.Serializer):
    recipient = serializers.CharField(max_length=64)
    amount = serializers.DecimalField(max_digits=20, decimal_places=8)
    signature = serializers.CharField()
