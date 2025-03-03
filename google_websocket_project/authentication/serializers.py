from rest_framework import serializers
from .models import GoogleAuth, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class GoogleAuthSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = GoogleAuth
        fields = ['user', 'google_id', 'token_expiry']
