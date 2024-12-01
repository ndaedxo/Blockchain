# DIDBlockchain/apps/api/secure_storage.py
from cryptography.hazmat.primitives import serialization
from django.contrib.auth import get_user_model


class SecureStorage:
    

    def store_private_key(self, username, private_key):
        CustomUser = get_user_model()
        # Serialize the private key to PEM format
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),  # Use encryption if needed
        )
        
        # Save the PEM bytes to the database
        user = CustomUser.objects.get(username=username)
        user.private_key = pem.decode('utf-8')  # Store as a string in the database
        user.save()

    def retrieve_private_key(self, username):
        CustomUser = get_user_model()
        # Implement logic to retrieve the private key for the given username
        user = CustomUser.objects.get(username=username)
        
        # Deserialize from PEM format back to an RSA private key
        pem = user.private_key.encode('utf-8')
        return serialization.load_pem_private_key(
            pem,
            password=None,  # Specify the password if using encryption
        )
