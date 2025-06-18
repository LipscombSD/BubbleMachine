from django.db import models
import uuid
from django.contrib.auth.models import User

from app import settings


class BubbleSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"BubbleSection {self.id} for user {self.user.email}"

class Bubble(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bubble_section = models.ForeignKey(BubbleSection, on_delete=models.CASCADE, related_name='bubbles')
    external_id = models.CharField(max_length=50)
    layer = models.CharField(max_length=10)
    bubble_name = models.CharField(max_length=100)
    start_time = models.DurationField()
    stop_time = models.DurationField()
    color = models.CharField(max_length=7)

    class Meta:
        unique_together = ['bubble_section', 'external_id']

    def __str__(self):
        return f"Bubble {self.external_id} in {self.bubble_section}"

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bubble_section = models.ForeignKey(BubbleSection, on_delete=models.CASCADE, related_name='comments')
    external_id = models.CharField(max_length=50)
    start_time = models.DurationField()
    end_time = models.DurationField()
    text = models.TextField()

    class Meta:
        unique_together = ['bubble_section', 'external_id']

    def __str__(self):
        return f"Comment {self.external_id} in {self.bubble_section}"