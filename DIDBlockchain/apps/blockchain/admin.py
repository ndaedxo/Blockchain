from django.contrib import admin
from .DIDDocument import   DIDDocumentService
from .models import DIDDocument, DIDResolutionMetadata , DIDTransaction,  Validator
from .transaction import Transaction

# admin.site.register(DIDDocumentService)
admin.site.register(DIDDocument)
admin.site.register(DIDResolutionMetadata)
admin.site.register(DIDTransaction)
admin.site.register(Transaction)
admin.site.register(Validator)