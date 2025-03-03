from django.urls import path
from . import views


urlpatterns = [
    path("connect/", views.connect_drive, name='connect-drive'),
    path("files/", views.list_files, name='list-files'),
    path('files/upload/', views.upload_files, name='upload-files'),
    path('files/<str:file_id>/download/', views.download_file, name='download-file'),
    path('picker/', views.get_picker_info, name='get-picker-info'),
]
