# DIDBlockchain\apps\blockchain\DIDDocument.py
from .models import DIDDocument as DIDDocumentModel, DIDResolutionMetadata, DIDTransaction
import json
import hashlib
from datetime import datetime
from django.core.exceptions import ValidationError
import logging  
import uuid

# Set up logging
logger = logging.getLogger(__name__)

class DIDDocumentService:
    def create_did(self, controller, public_key, authentication=None, service_endpoints=None):
        default_service_endpoints = [
            {
                "id": f"did:example:{uuid.uuid4().hex}#service-1",
                "type": "MessagingService",
                "serviceEndpoint": "https://example.com/messages"
            }
        ]
        try:
            did_doc = DIDDocumentModel.objects.create(
                controller=controller,
                public_key=public_key,
                authentication=authentication or [],
                service_endpoints=service_endpoints or default_service_endpoints
            )
            self._record_transaction(did_doc, 'CREATE', None, did_doc.to_dict())
            return did_doc
        except ValidationError as e:
            logger.error("Validation error while creating DID: %s", e)
            raise
        except Exception as e:
            logger.error("Failed to create DID Document: %s", e)
            raise

    def resolve_did(self, did, resolver="local"):
        try:
            did_doc = DIDDocumentModel.objects.get(did=did)
            DIDResolutionMetadata.objects.create(did=did_doc, resolver=resolver, success=True)
            return did_doc.to_dict()
        except DIDDocumentModel.DoesNotExist:
            DIDResolutionMetadata.objects.create(did=None, resolver=resolver, success=False, error=f"DID not found: {did}")
            raise Exception(f"DID not found: {did}")

    def update_did(self, did, updates, proof):
        try:
            did_doc = DIDDocumentModel.objects.get(did=did)
            previous_state = did_doc.to_dict()
            if not self._verify_proof(did_doc, proof):
                raise ValidationError("Invalid proof for DID update")
            for key, value in updates.items():
                if hasattr(did_doc, key):
                    setattr(did_doc, key, value)
            did_doc.save()
            self._record_transaction(did_doc, 'UPDATE', previous_state, did_doc.to_dict())
            return did_doc
        except DIDDocumentModel.DoesNotExist:
            raise Exception(f"DID not found: {did}")
        except ValidationError as e:
            logger.error("Validation error during DID update: %s", e)
            raise

    def deactivate_did(self, did, proof):
        try:
            did_doc = DIDDocumentModel.objects.get(did=did)
            previous_state = did_doc.to_dict()
            if not self._verify_proof(did_doc, proof):
                raise ValidationError("Invalid proof for DID deactivation")
            did_doc.deactivate()
            self._record_transaction(did_doc, 'DEACTIVATE', previous_state, did_doc.to_dict())
            return did_doc
        except DIDDocumentModel.DoesNotExist:
            raise Exception(f"DID not found: {did}")

    def _record_transaction(self, did_doc, operation, previous_state, new_state):
        transaction_data = {
            'did': did_doc.did,
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat(),
            'previous_state': previous_state,
            'new_state': new_state
        }
        transaction_hash = hashlib.sha256(json.dumps(transaction_data, sort_keys=True).encode()).hexdigest()
        DIDTransaction.objects.create(
            did_document=did_doc,
            operation=operation,
            previous_state=previous_state,
            new_state=new_state,
            transaction_hash=transaction_hash
        )

    def _verify_proof(self, did_doc, proof):
        try:
            signature = proof.get('proofValue')
            created = proof.get('created')
            if not signature or not created:
                raise ValidationError("Proof is missing required fields")
            message = f"{did_doc.did}:{created}"
            return True  # Replace with actual verification logic
        except Exception as e:
            logger.error("Proof verification failed: %s", e)
            return False
