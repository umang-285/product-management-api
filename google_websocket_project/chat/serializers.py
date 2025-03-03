from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp']
        read_only_fields = ['id', 'timestamp']
