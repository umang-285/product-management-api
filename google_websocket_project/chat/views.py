from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Message
from .serializers import MessageSerializer

User = get_user_model()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def message_list(request, user_id):
    """
        Get all messages between the logged-in user and another user.
    """
    messages = Message.objects.filter(
        sender=request.user, receiver=user_id
    ) | Message.objects.filter(
        sender=user_id, receiver=request.user
    ).order_by("timestamp")

    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_message(request):
    # Send message to another user
    receiver = request.data.get("receiver")
    content = request.data.get("content")

    if not receiver or not content:
        return Response({
            "error": "Receiver and content are required."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    receiver = get_object_or_404(User, id=receiver)
    message = Message.objects.create(
        sender=request.user,
        receiver=receiver,
        content=content
    )
    
    serializer = MessageSerializer(message)
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)
