import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from datetime import datetime, timedelta

from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from .models import GoogleAuth
from .serializers import UserSerializer

User = get_user_model()

def create_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        },
        scopes=settings.GOOGLE_SCOPE
    )

@api_view(["GET"])
def google_login(request):
    flow = create_flow()
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['state'] = state
    return Response({"authorization_url": authorization_url})

@api_view(["GET"])
def google_callback(request):
    state = request.session.get('state')

    flow = create_flow()
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    flow.fetch_token(
        authorization_response=request.build_absolute_uri(),
    )

    credentials = flow.credentials

    # Use the credentials to get user info
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()

    # Create or get user
    try:
        user = User.objects.get(email=user_info["email"])
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=user_info["email"],
            email=user_info["email"],
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", "")
        )
    
    # Create or Update Google Auth
    expiry = timezone.now() + timedelta(seconds=credentials.expiry.timestamp() - datetime.now().timestamp())
    google_auth, created = GoogleAuth.objects.update_or_create(
        user=user,
        defaults={
            "google_id": user_info["id"],
            "access_token": credentials.token,
            'refresh_token': credentials.refresh_token,
            "token_expiry": expiry,
        }
    )

    # Generate JWT Tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    # Here you'd typically create a session or JWT Token for the user
    # For simplicity, we'll just return the auth data
    return Response({
        "user": UserSerializer(user).data,
        "access_token": access_token,
        "refresh_token": str(refresh),
        "token_type": "Bearer",
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
