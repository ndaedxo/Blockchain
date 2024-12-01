# DIDBlockchain\apps\api\views.py
from django.shortcuts import get_object_or_404  # Add this import
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import api_view, permission_classes

from django.conf import settings
from .serializers.TransactionSerializer import TransactionSerializer
from .serializers.DIDDocumentSerializer import DIDDocumentSerializer
from .serializers.BlockSerializer import BlockSerializer
from apps.blockchain.models import DIDTransaction
from apps.api.serializers.DIDDocumentServiceSerializer import DIDTransactionSerializer
from .serializers.ValidatorSerializer import ValidatorSerializer, ValidatorRegistrationSerializer

from apps.blockchain.blockchain import Blockchain
from apps.blockchain.transaction import Transaction
from apps.blockchain.models import Validator as ValidatorModel
from apps.blockchain.DIDDocument import DIDDocumentService
from apps.blockchain.models import DIDDocument as DIDDocumentModel, DIDResolutionMetadata
from django.utils import timezone
from time import time
import logging  
from rest_framework import status
from django.core.exceptions import ValidationError



logger = logging.getLogger(__name__)

from rest_framework.views import APIView

class StatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        blockchain = Blockchain()
        stats = {
            'total_blocks': len(blockchain.chain),
            'total_transactions': DIDTransaction.objects.count(),
            'active_validators': len([v for v in blockchain.validators if v.is_active]),
            'pending_transactions': len(blockchain.pending_transactions),
        }
        return Response(stats)
    
class BlockViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """List all blocks"""
        blocks = Blockchain().chain  # Assuming this returns a list of blocks
        serializer = BlockSerializer(blocks, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Retrieve a specific block by index"""
        blockchain = Blockchain()
        try:
            block = blockchain.chain[int(pk)]
            serializer = BlockSerializer(block)
            return Response(serializer.data)
        except IndexError:
            return Response({"error": "Block not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def destroy(self, request, pk=None):
        """Delete a block by index (if applicable)"""
        return Response({"error": "Deleting blocks is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class BlockchainViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    blockchain = Blockchain()  # Ensure this instance is shared across requests in a real application

    def list(self, request):
        """Get the entire blockchain"""
        serializer = BlockSerializer(self.blockchain.chain, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get a specific block by index"""
        try:
            block = self.blockchain.chain[int(pk)]
            serializer = BlockSerializer(block)
            return Response(serializer.data)
        except IndexError:
            return Response(
                {"error": "Block not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def pending_transactions(self, request):
        """Get list of pending transactions"""
        serializer = TransactionSerializer(
            self.blockchain.pending_transactions, 
            many=True
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def chain_status(self, request):
        """Get current status of the blockchain"""
        return Response({
            'length': len(self.blockchain.chain),
            'last_block': BlockSerializer(self.blockchain.get_last_block()).data,
            'pending_transactions': len(self.blockchain.pending_transactions)
        })
    
    @action(detail=False, methods=['get'], url_path='blockchain-info')
    def blockchain_info(self, request):
        """Get blockchain information."""
        info = {
            'chain_length': len(self.blockchain.chain),
            'last_block': BlockSerializer(self.blockchain.get_last_block()).data,
            'pending_transactions': len(self.blockchain.pending_transactions)
        }
        return Response(info)


class TransactionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DIDTransaction.objects.all()
    serializer_class = DIDTransactionSerializer

    def list(self, request, *args, **kwargs):
        """
        List all transactions related to DIDs.
        You can filter transactions by DID using a query parameter.
        """
        did = request.query_params.get('did', None)
        if did:
            # Filter transactions by the provided DID
            transactions = self.queryset.filter(did_document__did=did)
        else:
            # Get all transactions
            transactions = self.queryset
        
        # Serialize the transaction data
        serializer = self.serializer_class(transactions, many=True)  # Use the defined serializer_class
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Retrieve a specific transaction by its ID."""
        transaction = get_object_or_404(DIDTransaction, id=pk)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    def create(self, request):
        serializer = TransactionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Save the transaction to the database
            transaction = serializer.save()

            # Create a new Transaction object for the blockchain
            blockchain = Blockchain()
            blockchain.add_pending_transaction(transaction)  # This method needs to be implemented in Blockchain

            # Create a response payload
            response_data = {
                'transaction_id': transaction.id,
                'sender': transaction.sender,
                'recipient': transaction.recipient,
                'timestamp': timezone.now().timestamp(),
                'signature': transaction.signature.hex() if transaction.signature else None,
            }

            # Log the transaction creation event
            logger.info(f'Transaction created: {response_data}')

            # Return a successful response with transaction details
            return Response(response_data, status=status.HTTP_201_CREATED)

        # Return error response if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Delete a transaction by ID."""
        transaction = get_object_or_404(DIDTransaction, id=pk)  # Ensure you're using the correct model
        transaction.delete()
        return Response({"message": "Transaction deleted"}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        """Update a transaction by ID."""
        transaction = get_object_or_404(DIDTransaction, id=pk)  # Ensure you're using the correct model
        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DIDBlockchain\apps\api\views.py
from django.shortcuts import get_object_or_404  # Add this import
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import api_view, permission_classes

from django.conf import settings
from .serializers.TransactionSerializer import TransactionSerializer
from .serializers.DIDDocumentSerializer import DIDDocumentSerializer
from .serializers.BlockSerializer import BlockSerializer
from apps.blockchain.models import DIDTransaction
from apps.api.serializers.DIDDocumentServiceSerializer import DIDTransactionSerializer
from .serializers.ValidatorSerializer import ValidatorSerializer, ValidatorRegistrationSerializer

from apps.blockchain.blockchain import Blockchain
from apps.blockchain.transaction import Transaction
from apps.blockchain.models import Validator as ValidatorModel
from apps.blockchain.DIDDocument import DIDDocumentService
from apps.blockchain.models import DIDDocument as DIDDocumentModel, DIDResolutionMetadata
from django.utils import timezone
from time import time
import logging  
from rest_framework import status
from django.core.exceptions import ValidationError
from apps.users.models import CustomUser

from apps.blockchain.validator import Validator

logger = logging.getLogger(__name__)

class ValidatorViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    minimum_stake = 50.0 
    def list(self, request):
        validators = ValidatorModel.objects.all()
        serializer = ValidatorSerializer(validators, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        validator = get_object_or_404(ValidatorModel, pk=pk)
        serializer = ValidatorSerializer(validator)
        return Response(serializer.data)

    
    def create(self, request):
        serializer = ValidatorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Fetch the user by username or public_key
            username = request.user.username
            user = get_object_or_404(CustomUser, username=username)

            validator = ValidatorModel(
                address=user.username,  # Use the username of the user
                stake=serializer.validated_data['stake'],
                public_key=serializer.validated_data['public_key'],
                private_key=user.private_key,  # Use the user's private key
            )
            validator.save()
            return Response(ValidatorSerializer(validator).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        validator = get_object_or_404(ValidatorModel, pk=pk)
        serializer = ValidatorSerializer(validator, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        validator = get_object_or_404(ValidatorModel, pk=pk)
        validator.delete()
        return Response({"message": "Validator deleted"}, status=status.HTTP_204_NO_CONTENT)
     

    # Inside any method that initiates validation:
    @action(detail=True, methods=['post'])
    def initiate_validation(self, request, pk=None):
        validator_instance = get_object_or_404(ValidatorModel, pk=pk)
        validator = Validator(
            address=validator_instance.address,
            stake=validator_instance.stake,
            public_key=validator_instance.public_key,
            private_key=validator_instance.private_key  # Should fetch the actual private key here
        )



        if not validator.has_sufficient_stake(self.minimum_stake):
            return Response({"error": "Insufficient stake for validation"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the pending transactions
        blockchain = Blockchain()  # or however your blockchain instance is accessed
        transactions = blockchain.pending_transactions

        # Prepare block data
        block_data = {
            "index": len(blockchain.chain),  # Automatically set index based on current chain length
            "transactions": transactions,
            "previous_hash": blockchain.get_last_block().hash,
            "validator": request.user.username,  # Current user as validator
            "nonce": 0
        }

        # Serialize and save
        block_serializer = BlockSerializer(data=block_data, context={'request': request})
        if block_serializer.is_valid():
            block = block_serializer.save()
            
            # Generate a real signature
            validator_signature = validator.sign(block.hash)  # Ensure this method exists and correctly signs the block hash
            blockchain.add_block(block, validator_signature=validator_signature)  # Use real signature
            
            return Response(block_serializer.data, status=status.HTTP_201_CREATED)
        return Response(block_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Extra Options - Custom Actions
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle the 'is_active' status of a validator."""
        validator = get_object_or_404(ValidatorModel, pk=pk)
        validator.is_active = not validator.is_active
        validator.save()
        logger.info(f"Validator {validator.address} toggled active status to {validator.is_active}.")
        return Response({"is_active": validator.is_active}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reset_reputation(self, request, pk=None):
        """Reset the reputation score of a validator."""
        validator = get_object_or_404(ValidatorModel, pk=pk)
        validator.reputation_score = 0.0
        validator.save()
        logger.info(f"Validator {validator.address} reset reputation score to 0.")
        return Response({"reputation_score": validator.reputation_score}, status=status.HTTP_200_OK)



class DIDDocumentViewSet(viewsets.ModelViewSet):
    queryset = DIDDocumentModel.objects.all()
    serializer_class = DIDDocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Handle creation of a new DID Document using the current user's public key and DID."""
        try:
            # Retrieve the user's public key and DID
            public_key = self.request.user.public_key  # Ensure `public_key` exists in `User`
            did = self.request.user.did
            
            # Define default service endpoints if needed
            service_endpoints = [
                {
                    "id": f"{did}#messaging",  # Adding fragment identifier for the service endpoint
                    "type": "MessagingService",
                    "serviceEndpoint": "https://example.com/messages"
                }
            ]

            # Pass the controller, public key, and service endpoints to the serializer
            serializer.save(controller=self.request.user, public_key=public_key, service_endpoints=service_endpoints)
        except AttributeError:
            logger.error("Current user has no public key or DID set.")
            return Response({"error": "User's public key or DID not found."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error("Error creating DID Document: %s", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Update an existing DID Document."""
        did_document = get_object_or_404(DIDDocumentModel, pk=pk)
        serializer = self.get_serializer(did_document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Delete a DID Document by ID."""
        did_document = get_object_or_404(DIDDocumentModel, pk=pk)
        did_document.delete()
        return Response({"message": "DID Document deleted"}, status=status.HTTP_204_NO_CONTENT)

    @api_view(['POST'])
    def create_transaction(request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Create and broadcast transaction
                blockchain = Blockchain()
                transaction = Transaction(**serializer.validated_data)
                blockchain.add_pending_transaction(transaction)  # Implement this method in Blockchain class
                return Response({"message": "Transaction created"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error("Error creating transaction: %s", e)
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_service_endpoint(self, request, pk=None):
        did_document = get_object_or_404(DIDDocumentModel, pk=pk)
        type_name = request.data.get("type")
        endpoint = request.data.get("serviceEndpoint")
        if not type_name or not endpoint:
            return Response({"error": "Both type and serviceEndpoint are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            did_document.add_service_endpoint(type_name, endpoint)
            return Response({"message": "Service endpoint added successfully"}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": e.message_dict}, status=status.HTTP_400_BAD_REQUEST)
