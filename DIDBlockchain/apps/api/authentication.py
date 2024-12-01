# api/authentication.py
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from cryptography.hazmat.primitives import serialization

CustomUser = get_user_model()

class BlockchainAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            # Extract the token from the header
            auth_type, token = auth_header.split()
            if auth_type.lower() != 'bearer':
                return None

            # Validate the token and get the user
            user = self.get_user_from_token(token)
            
            # Attach blockchain-specific attributes to the user
            self.attach_blockchain_attributes(user)
            
            return (user, None)
        except Exception as e:
            raise exceptions.AuthenticationFailed('Invalid token.')

    def get_user_from_token(self, token):
        """
        Validate the token and return the corresponding user.
        In production, this would verify the token.
        """
        try:
            # Decoding the token and retrieving the user (simplified example)
            user = CustomUser.objects.get(username='example_user')
            return user
        except CustomUser.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

    def attach_blockchain_attributes(self, user):
        """
        Attach blockchain-specific attributes (like public_key, wallet_address) to the user object.
        These would be retrieved securely from the user model.
        """
        user.public_key = user.public_key
        user.wallet_address = user.wallet_address

        # Attach method to return public key in PEM format
        def get_public_key_pem(self):
            return self.public_key

        user.get_public_key_pem = get_public_key_pem.__get__(user)
