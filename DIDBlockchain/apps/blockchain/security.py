# DIDBlockchain\apps\blockchain\security.py
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import hashlib
import json
import base64

class SecurityManager:
    def __init__(self):
        self.hash_algorithm = hashes.SHA256()

    def generate_key_pair(self):
        """Generate a new RSA key pair for digital signatures"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        return private_key, public_key

    def serialize_public_key(self, public_key):
        """Serialize public key to PEM format"""
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def serialize_private_key(self, private_key):
        """Serialize private key to PEM format"""
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode('utf-8')

    def calculate_hash(self, data):
        """Calculate SHA256 hash of data"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(str(data).encode()).hexdigest()

    def sign_data(self, private_key, data):
        """Sign data using private key"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        
        signature = private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    def verify_signature(self, public_key, signature, data):
        """Verify signature using public key"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data, sort_keys=True)
            
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            public_key.verify(
                signature_bytes,
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def merkle_root(self, transactions):
        """Calculate Merkle root of transactions"""
        if not transactions:
            return None

        leaves = [self.calculate_hash(tx) for tx in transactions]
        
        while len(leaves) > 1:
            if len(leaves) % 2 != 0:
                leaves.append(leaves[-1])
            
            next_level = []
            for i in range(0, len(leaves), 2):
                combined = leaves[i] + leaves[i+1]
                next_level.append(self.calculate_hash(combined))
            leaves = next_level

        return leaves[0] if leaves else None