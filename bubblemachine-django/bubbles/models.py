from django.db import models
import uuid
from django.contrib.auth.models import User

from app import settings


class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    song_hash = models.CharField(max_length=64, unique=True)  # SHA-256 hash
    title = models.CharField(max_length=255, blank=True, null=True)
    artist = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'song_hash']

    def __str__(self):
        return f"Song {self.song_hash[:8]}... for user {self.user.email}"


class Bubble(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='bubbles')
    external_id = models.CharField(max_length=50)  # The "id" field from frontend
    layer = models.CharField(max_length=10)
    bubble_name = models.CharField(max_length=100)
    start_time = models.DurationField()
    stop_time = models.DurationField()
    color = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['song', 'external_id']

    def __str__(self):
        return f"Bubble {self.external_id} for song {self.song.song_hash[:8]}..."


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='comments')
    external_id = models.CharField(max_length=50)  # The "id" field from frontend
    start_time = models.DurationField()
    end_time = models.DurationField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['song', 'external_id']

    def __str__(self):
        return f"Comment {self.external_id} for song {self.song.song_hash[:8]}..."


# Remove BubbleSection model - no longer needed