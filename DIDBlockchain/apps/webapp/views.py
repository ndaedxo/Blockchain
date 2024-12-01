# webapp/views.py
import json
import requests
import logging
from requests.exceptions import RequestException
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.contrib.auth import authenticate, login, get_user_model
from django.views import View
from django.contrib import messages
from django.db import IntegrityError
from rest_framework.authtoken.models import Token

from apps.api.serializers.TransactionSerializer import TransactionSerializer
from apps.api.serializers.ValidatorSerializer import ValidatorSerializer
from apps.wallet.models import Wallet

CustomUser = get_user_model()


# Utility function for making safe API calls with error handling
def safe_api_call(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for non-200 status codes
        return response.json()
    except RequestException as e:
        logging.error(f"API call failed: {e}")
        return None


# Mixin for ensuring the user has an auth_token
class AuthTokenRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure users have a valid auth_token."""
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'auth_token'):
            messages.error(request, "User does not have an authentication token.")
            return redirect('login')  # Redirect to the login page instead of error page
        return super().dispatch(request, *args, **kwargs)

from django.http import JsonResponse

def placeholder_view(request, id1, id2):
    # Example logic here
    return JsonResponse({'message': 'Placeholder response', 'id1': id1, 'id2': id2})

class DashboardView(AuthTokenRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = getattr(self.request.user, 'auth_token', None)

        # Fetch dashboard stats from the API
        if token:
            response = requests.get('http://localhost:8000/api/stats/', headers={'Authorization': f'Token {token}'})
            if response.status_code == 200:
                stats = response.json()
                active_validators = stats.get('active_validators', [])

                # Check if active_validators is a list before checking membership
                if isinstance(active_validators, list):
                    context['is_validator'] = self.request.user.username in active_validators
                else:
                    context['is_validator'] = False  # Handle the unexpected type

                context.update({
                    'chain_length': stats.get('total_blocks'),
                    'pending_transactions': stats.get('pending_transactions'),
                    'recent_blocks': stats.get('recent_blocks', []),
                })
            else:
                context['error'] = "Failed to fetch dashboard stats."
        else:
            context['error'] = "User is not authenticated."
        return context


class BlockListView(AuthTokenRequiredMixin, ListView):
    template_name = "blocks.html"
    context_object_name = "blocks"
    paginate_by = 20

    def get_queryset(self):
        api_url = 'http://localhost:8000/api/blocks/'
        headers = {'Authorization': f'Token {self.request.user.auth_token}'}
        blocks = safe_api_call(api_url, headers)
        return blocks if blocks else []


class BlockDetailView(AuthTokenRequiredMixin, DetailView):
    template_name = "block_detail.html"
    context_object_name = "block"

    def get_object(self):
        index = self.kwargs.get('index')
        api_url = f'http://localhost:8000/api/blocks/{index}/'
        headers = {'Authorization': f'Token {self.request.user.auth_token}'}
        block = safe_api_call(api_url, headers)
        if block:
            return block
        raise Http404("Block not found")


class TransactionListView(AuthTokenRequiredMixin, ListView):
    template_name = "transactions.html"
    context_object_name = "transactions"
    paginate_by = 20

    def get_queryset(self):
        api_url = 'http://localhost:8000/api/transactions/'
        headers = {'Authorization': f'Token {self.request.user.auth_token}'}
        transactions = safe_api_call(api_url, headers)
        return transactions if transactions else []


class TransactionDetailView(AuthTokenRequiredMixin, DetailView):
    template_name = "transaction_detail.html"
    context_object_name = "transaction"

    def get_object(self):
        transaction_id = self.kwargs.get('id')
        api_url = f'http://localhost:8000/api/transactions/{transaction_id}/'
        headers = {'Authorization': f'Token {self.request.user.auth_token}'}
        transaction = safe_api_call(api_url, headers)
        if transaction:
            return transaction
        raise Http404("Transaction not found")


class ValidatorListView(AuthTokenRequiredMixin, ListView):
    template_name = "validators.html"
    context_object_name = "validators"
    paginate_by = 20

    def get_queryset(self):
        api_url = 'http://localhost:8000/api/validators/'
        headers = {'Authorization': f'Token {self.request.user.auth_token}'}
        validators = safe_api_call(api_url, headers)
        return validators if validators else []


class ValidatorDetailView(AuthTokenRequiredMixin, DetailView):
    template_name = "validator_detail.html"
    context_object_name = "validator"

    def get_object(self):
        validator_id = self.kwargs.get('id')
        api_url = f'http://localhost:8000/api/validators/{validator_id}/'
        headers = {'Authorization': f'Token {self.request.user.auth_token}'}
        validator = safe_api_call(api_url, headers)
        if validator:
            return validator
        raise Http404("Validator not found")



class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)  # Get existing token or create new one
            return JsonResponse({'success': True, 'token': token.key})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid credentials'}, status=401)

 



class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        api_url = 'http://localhost:8000/users/'  # Adjust based on your URL routing
        data = json.loads(request.body)

        # Validate input data
        username = data.get('username')
        email = data.get('email')  # Get email
        password = data.get('password')

        if not username or not email or not password:
            return JsonResponse({'success': False, 'message': 'Username, email, and password are required.'}, status=400)

        if len(password) < 6:  # Example validation
            return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters long.'}, status=400)

        # Make a request to the UserCreateView to create a new user
        try:
            response = requests.post(api_url, json={'username': username, 'email': email, 'password': password})
            if response.status_code == 201:
                return JsonResponse({'success': True, 'message': 'User created successfully.'})
            else:
                return JsonResponse(response.json(), status=response.status_code)  # Return the error from the API
        except requests.exceptions.RequestException as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)


def users_list(request):
    users = CustomUser.objects.all()
    return render(request, 'users.html', {'users': users})

class UserDetailView(View):
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        return render(request, 'user_detail.html', {'user': user})
    
class WalletView(AuthTokenRequiredMixin, TemplateView):
    template_name = "wallet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet = get_object_or_404(Wallet, user=self.request.user)
        context['balance'] = float(wallet.balance)
        context['transactions'] = wallet.transaction_history  # Assuming it's already in the wallet model
        context['wallet_address'] = wallet.wallet_address
        return context
