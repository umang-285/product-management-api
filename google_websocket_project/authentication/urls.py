from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .views import google_login, google_callback, get_current_user

urlpatterns = [
    path("google/login/", google_login, name="google-login"),
    path("google/callback/", google_callback, name="google-callback"),
    path("user/me/", get_current_user, name="current-user"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('login/', TokenObtainPairView.as_view(), name='auth-token'),
]
