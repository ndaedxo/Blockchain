# DIDBlockchain/apps/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlockchainViewSet,
    TransactionViewSet,
    ValidatorViewSet,
    DIDDocumentViewSet,
    BlockViewSet,
    StatsView,  # Import the new StatsView
)
from apps.wallet.views import WalletViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'blockchain', BlockchainViewSet, basename='blockchain')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'validators', ValidatorViewSet, basename='validator')
router.register(r'did-documents', DIDDocumentViewSet, basename='did-document')
router.register(r'blocks', BlockViewSet, basename='block')
router.register(r'wallets', WalletViewSet, basename='wallet')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='api-auth')),  # Add namespace here
    path('stats/', StatsView.as_view(), name='stats'),  # Add this line for the stats endpoint
]
