# Blockchain\DIDBlockchain\webapp\urls.py
from apps.wallet.views import WalletViewSet 
from django.urls import path
from .views import (
    TransactionListView,
    ValidatorListView,
    LoginView,
    RegisterView,
    BlockListView,
    DashboardView,
    BlockDetailView,
    TransactionDetailView,
    ValidatorDetailView,
    # user_detail,
    UserDetailView,
    users_list,
    WalletView,
    placeholder_view
)

# In webapp/urls.py
from django.shortcuts import render
urlpatterns = [
    path('api/placeholder/<int:id1>/<int:id2>/', placeholder_view, name='placeholder_view'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('blocks/', BlockListView.as_view(), name='blocks'),
    path('blocks/<int:index>/', BlockDetailView.as_view(), name='block_detail'),
    path('transactions/', TransactionListView.as_view(), name='transactions'),
    path('transactions/<int:id>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('validators/', ValidatorListView.as_view(), name='validators'),
    path('validators/<int:id>/', ValidatorDetailView.as_view(), name='validator_detail'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('users/', users_list, name='users'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('api/wallet/', WalletViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/wallet/add-funds/', WalletViewSet.as_view({'post': 'add_funds'})),
    path('api/wallet/transfer-funds/', WalletViewSet.as_view({'post': 'transfer_funds'})),
    path('api/wallet/withdraw-funds/', WalletViewSet.as_view({'post': 'withdraw_funds'})),
    path('wallet/', WalletView.as_view(), name='wallet'),
    # Removed the error page URL
]
