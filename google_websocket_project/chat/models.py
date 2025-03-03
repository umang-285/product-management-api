from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recieve_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.content[:20]}"
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=["sender", "receiver", "timestamp"]),
            models.Index(fields=["receiver", "is_read"])
        ]
