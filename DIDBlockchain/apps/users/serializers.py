# DIDBlockchain\apps\users\serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate, login
CustomUser = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password','private_key',
            'public_key', 'wallet_address', 'did','role', 'status',
            'profile_picture', 'social_media_links', 'reputation_score',
            'multi_signature_requirements', 'last_active_timestamp'
        ]
        read_only_fields = ['id','private_key', 'public_key', 'wallet_address', 'reputation_score', 'last_active_timestamp']
        extra_kwargs = {
            'password': {'write_only': True},  # Password should only be provided for creation
        }

    def create(self, validated_data):
        # Delegate user creation to the manager, ensuring password and key handling
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'user'),  # Default role is 'user'
            status=validated_data.get('status', 'active'),
            profile_picture=validated_data.get('profile_picture'),
            social_media_links=validated_data.get('social_media_links', {}),
            multi_signature_requirements=validated_data.get('multi_signature_requirements', {}),
        )
        return user

    def update(self, instance, validated_data):
        # Allow updating non-sensitive fields, except for password
        
        non_sensitive_fields = ['username', 'email', 'role', 'status', 'profile_picture', 'social_media_links']
        for field in non_sensitive_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance



