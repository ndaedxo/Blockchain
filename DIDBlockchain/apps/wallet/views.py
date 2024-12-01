# DIDBlockchain\apps\wallet\views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal, InvalidOperation
import logging
from apps.api.serializers.TransactionSerializer import TransactionSerializer  # Import CreateTransactionSerializer
from apps.blockchain.models import DIDTransaction
from .models import Wallet
from .serializers import WalletSerializer
from apps.blockchain.blockchain import Blockchain  # For blockchain transaction handling
from rest_framework.permissions import IsAuthenticated
import logging
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from time import time
logger = logging.getLogger(__name__)

class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='add-funds')
    def add_funds(self, request):
        try:
            amount = Decimal(request.data.get('amount'))
        except (TypeError, ValueError, InvalidOperation):
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        wallet = request.user.wallet
        wallet.balance += amount
        wallet.save()

        # Create the transaction using the CreateTransactionSerializer
        transaction_data = {
            "recipient": wallet.wallet_address,
            "fee": float(amount),
        }
        transaction_serializer = TransactionSerializer(data=transaction_data, context={'request': request})
        
        if transaction_serializer.is_valid():
            # Save the transaction to the database
            transaction = transaction_serializer.save()

            # Add transaction to blockchain
            blockchain = Blockchain()
            blockchain.add_pending_transaction(transaction)

            # Create response data
            response_data = {
                'transaction_id': transaction.id,
                'recipient': transaction.recipient,
                'fee': transaction.fee,
                'timestamp': timezone.now().timestamp(),
                'signature': transaction.signature.hex() if transaction.signature else None,
            }
            if wallet.transaction_history is None:
                wallet.transaction_history = []  # Initialize if it doesn't exist
                
            wallet.transaction_history.append(response_data)
            wallet.save()

            # Log the transaction creation
            logger.info(f'Funds added: {response_data}')

            return Response({"message": "Funds added successfully", "new_balance": float(wallet.balance)}, status=status.HTTP_201_CREATED)
        
        return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='transfer-funds')
    def transfer_funds(self, request):
        recipient_address = request.data.get('recipient_address')

        logger.debug(f"Attempting to transfer funds to address: {recipient_address}")

        try:
            amount = Decimal(request.data.get('amount'))
        except (TypeError, ValueError, InvalidOperation):
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        wallet = request.user.wallet

        if wallet.balance < amount:
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            recipient_wallet = Wallet.objects.get(wallet_address=recipient_address)
            logger.debug(f"Found recipient wallet: {recipient_wallet}")

            # Create the transaction using the TransactionSerializer
            transaction_data = {
                "recipient": recipient_wallet.wallet_address,
                "fee": float(amount),
            }
            transaction_serializer = TransactionSerializer(data=transaction_data, context={'request': request})
            
            if transaction_serializer.is_valid():
                # Perform the transfer
                wallet.balance -= amount
                recipient_wallet.balance += amount
                
                # Save the updated balances
                wallet.save()
                recipient_wallet.save()

                # Save the transaction to the database
                transaction = transaction_serializer.save()
                
                # Add transaction to blockchain
                blockchain = Blockchain()
                blockchain.add_pending_transaction(transaction)

                # Create response data
                response_data = {
                    'transaction_id': transaction.id,
                    'sender': transaction.sender,
                    'recipient': transaction.recipient,
                    'fee': transaction.fee,
                    'timestamp': timezone.now().timestamp(),
                    'signature': transaction.signature.hex() if transaction.signature else None,
                }

                # Append to transaction history (assuming it's a JSONField or list)
                if wallet.transaction_history is None:
                    wallet.transaction_history = []  # Initialize if it doesn't exist
                
                wallet.transaction_history.append(response_data)
                wallet.save()

                if recipient_wallet.transaction_history is None:
                    recipient_wallet.transaction_history = []  # Initialize if it doesn't exist
                
                recipient_wallet.transaction_history.append(response_data)
                recipient_wallet.save()

                # Log the transfer
                logger.info(f'Transfer successful: {response_data}')

                return Response({"message": "Transfer successful", "new_balance": float(wallet.balance)}, status=status.HTTP_201_CREATED)
            
            return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Wallet.DoesNotExist:
            logger.error(f"Recipient wallet not found for address: {recipient_address}")
            return Response({"error": "Recipient wallet not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='withdraw-funds')
    def withdraw_funds(self, request):
        try:
            amount = Decimal(request.data.get('amount'))
        except (TypeError, ValueError, InvalidOperation):
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        wallet = request.user.wallet

        if wallet.balance < amount:
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct the amount from the user's wallet balance
        wallet.balance -= amount
        wallet.save()

        # Create the withdrawal transaction using the TransactionSerializer
        transaction_data = {
            "recipient": wallet.wallet_address,  # Since it's a withdrawal, there's no specific recipient
            "fee": float(amount),
        }
        transaction_serializer = TransactionSerializer(data=transaction_data, context={'request': request})

        if transaction_serializer.is_valid():
            # Save the transaction to the database
            transaction = transaction_serializer.save()

            # Add transaction to blockchain
            blockchain = Blockchain()
            blockchain.add_pending_transaction(transaction)

            # Create response data
            response_data = {
                'transaction_id': transaction.id,
                'recipient': transaction.recipient,
                'fee': transaction.fee,
                'timestamp': timezone.now().timestamp(),
                'signature': transaction.signature.hex() if transaction.signature else None,
            }

            # Append to transaction history
            if wallet.transaction_history is None:
                wallet.transaction_history = []  # Initialize if it doesn't exist

            wallet.transaction_history.append(response_data)
            wallet.save()

            # Log the withdrawal
            logger.info(f'Withdrawal successful: {response_data}')

            return Response({"message": "Withdrawal successful", "new_balance": float(wallet.balance)}, status=status.HTTP_201_CREATED)

        return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)