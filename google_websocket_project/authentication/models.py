from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class GoogleAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_id = models.CharField(max_length=100)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}'s Google Auth"
