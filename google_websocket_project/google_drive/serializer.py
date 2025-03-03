from rest_framework import serializers
from .models import GoogleDriveFile


class GoogleDriveFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleDriveFile
        fields = ['id', 'file_id', 'name', 'mime_type', 'web_link_type', 'created_at']
        read_only_fields = ['id', 'created_at']
