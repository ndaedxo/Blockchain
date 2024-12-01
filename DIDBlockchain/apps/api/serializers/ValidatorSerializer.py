# DIDBlockchain\apps\api\serializers\ValidatorSerializer.py
from rest_framework import serializers
from apps.blockchain.models import Validator

class ValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validator
        fields = [
            'id',
            'address', 
            'public_key', 
            'stake', 
            'is_active',  # Ensure these fields exist in the model
            'last_block_validated', 
            'reputation_score', 
            'rewards',
            'private_key'
        ]

class ValidatorRegistrationSerializer(serializers.Serializer):
    stake = serializers.DecimalField(max_digits=20, decimal_places=8)
    public_key = serializers.CharField()

    def validate_stake(self, value):
        if value <= 0:
            raise serializers.ValidationError("Stake amount must be greater than 0")
        return value

    def validate_public_key(self, value):
        if not value:  # Example basic check
            raise serializers.ValidationError("Public key is required")
        return value

