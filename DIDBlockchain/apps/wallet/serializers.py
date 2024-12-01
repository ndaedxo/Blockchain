# DIDBlockchain/apps/wallet/serializers.py
from rest_framework import serializers
from .models import Wallet
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'wallet_address', 'balance', 'transaction_history']
        read_only_fields = ['id','user', 'balance','wallet_address', 'transaction_history']  # User and balance are managed by backend

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['balance'] = float(instance.balance)  # Convert Decimal to float
        return representation
