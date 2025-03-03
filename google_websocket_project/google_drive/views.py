import io
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from authentication.models import GoogleAuth
from .models import GoogleDriveFile
from .serializer import GoogleDriveFileSerializer


def get_drive_service(user):
    try:
        google_auth = GoogleAuth.objects.get(user=user)
        credentials = Credentials(
            token=google_auth.access_token,
            refresh_token=google_auth.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET
        )
        return build('drive', 'v3', credentials=credentials)
    except GoogleAuth.DoesNotExist:
        return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def connect_drive(request):
    drive_service = get_drive_service(request.user)
    if not drive_service:
        return Response({
            "error": "Google Drive not connected. Please authenticate with Google first."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Test connection by listing files
    files = drive_service.files().list(pageSize=10).execute()

    return Response({
        "status": "connected",
        "message": "Successfully connected to Google Drive"
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_files(request):
    drive_service = get_drive_service(request.user)
    if not drive_service:
        return Response({
            "error": "Google Drive not connected. Please authenticate with Google first."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # List files from Google Drive
    results = drive_service.files().list(
        pageSize=10,
        fields="nextPageToken, files(id, name, mimeType, webViewLink)"
    ).execute()

    files = results.get("files", [])

    # Save files to our database
    for file in files:
        GoogleDriveFile.objects.update_or_create(
            user=request.user,
            file_id=file['id'],
            defaults={
                'name': file['name'],
                'mime_type': file['mimeType'],
                'web_link_type': file.get('webViewLink', '')
            }
        )
    
    # Get updated list from our database
    user_files = GoogleDriveFile.objects.filter(user=request.user)
    serializer = GoogleDriveFileSerializer(user_files, many=True)

    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_files(request):
    drive_service = get_drive_service(request.user)
    if not drive_service:
        return Response({
            "error": "Google Drive not connected. Please authenticate with Google first."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if 'file' not in request.FILES:
        return Response({
            "error": "No file provided"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']

    # Save file temporarily
    file_path = f"tmp/{file.name}"
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    # Upload to Google Drive
    file_metadata = {
        'name': file.name
    }

    media = MediaFileUpload(file_path, resumable=True)
    drive_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, mimeType, webViewLink'
    ).execute()

    # Save to our database
    db_file = GoogleDriveFile.objects.create(
        user=request.user,
        file_id=drive_file['id'],
        name=drive_file['name'],
        mime_type=drive_file['mimeType'],
        web_link_type=drive_file.get('webViewLink', ''),
    )

    serializer = GoogleDriveFileSerializer(db_file)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_file(request, file_id):
    drive_service = get_drive_service(request.user)
    if not drive_service:
        return Response({
            "error": "Google Drive not connected. Please authenticate with Google first."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get file metadata
    file = get_object_or_404(GoogleDriveFile, user=request.user, file_id=file_id)

    # Download file from Google Drive
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
    
    # Return file as response
    response = HttpResponse(
        fh.getvalue(),
        content_type="application/octet-stream"
    )

    response['Content-Disposition'] = f'attachment; filename="{file.name}"'
    return response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_picker_info(request):
    # Return information needed for the Google Picker API
    try:
        google_auth = GoogleAuth.objects.get(user=request.user)

        return Response({
            "developerKey": settings.GOOGLE_API_KEY,
            "clientId": settings.GOOGLE_CLIENT_ID,
            "scope": settings.GOOGLE_SCOPE,
            "authToken": google_auth.access_token
        })
    except GoogleAuth.DoesNotExist:
        return Response({
            "error": "Google not authenticated. Please authenticate with Google first."
        }, status=status.HTTP_400_BAD_REQUEST)
