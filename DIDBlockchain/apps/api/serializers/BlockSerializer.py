# DIDBlockchain\apps\api\serializers\BlockSerializer.py
import time
import hashlib
import json
from rest_framework import serializers
from apps.blockchain.block import Block
from apps.blockchain.transaction import Transaction
from .TransactionSerializer import TransactionSerializer

class BlockSerializer(serializers.Serializer):
    # Serializer fields
    index = serializers.IntegerField()
    transactions = TransactionSerializer(many=True, required=False)
    timestamp = serializers.FloatField(required=False)
    previous_hash = serializers.CharField()
    validator = serializers.CharField(required=False)
    nonce = serializers.IntegerField()
    hash = serializers.CharField(read_only=True)  # This field is read-only

    def create(self, validated_data):
        # Set default values if not provided
        validated_data['timestamp'] = validated_data.get('timestamp', time.time())
        validated_data['validator'] = validated_data.get('validator', self.context['request'].user.username)

        # Handle transactions
        transactions_data = validated_data.pop('transactions', [])
        transactions = [Transaction(**tx_data) for tx_data in transactions_data]

        # Create Block instance
        block = Block(**validated_data, transactions=transactions)

        # Finalize the block to calculate the hash
        block.finalize_block()

        return block
