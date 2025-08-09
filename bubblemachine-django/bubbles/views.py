from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from users.views import subscription_or_trial_permission
from .models import Song, Bubble, Comment
from .serializers import (
    SongSerializer,
    SongWithDataSerializer,
    BubbleSerializer,
    CommentSerializer
)


class SongViewSet(viewsets.ModelViewSet):
    serializer_class = SongSerializer
    permission_classes = [IsAuthenticated, subscription_or_trial_permission(require_subscription=True)]

    def get_queryset(self):
        return Song.objects.filter(user=self.request.user).order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def find_or_create(self, request):
        """Find or create a song by hash"""
        song_hash = request.data.get('song_hash')
        if not song_hash:
            return Response(
                {'error': 'song_hash is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        song, created = Song.objects.get_or_create(
            song_hash=song_hash,
            defaults={
                'user': request.user,
                'title': request.data.get('title', ''),
                'artist': request.data.get('artist', '')
            }
        )

        serializer = SongSerializer(song)
        return Response({
            'song': serializer.data,
            'created': created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get bubbles and comments for a specific song"""
        song = self.get_object()
        serializer = SongWithDataSerializer(song)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_hash(self, request):
        """Get a song and its data by hash"""
        song_hash = request.query_params.get('hash')
        if not song_hash:
            return Response(
                {'error': 'hash parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            song = Song.objects.get(song_hash=song_hash, user=request.user)
            serializer = SongWithDataSerializer(song)
            return Response(serializer.data)
        except Song.DoesNotExist:
            return Response(
                {'error': 'Song not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class BubbleViewSet(viewsets.ModelViewSet):
    serializer_class = BubbleSerializer
    permission_classes = [IsAuthenticated, subscription_or_trial_permission(require_subscription=True)]

    def get_queryset(self):
        # Filter by song if provided
        song_uuid = self.request.query_params.get('song_uuid')
        if song_uuid:
            return Bubble.objects.filter(song__user=self.request.user, song_id=song_uuid)
        return Bubble.objects.filter(song__user=self.request.user)

    def perform_create(self, serializer):
        song_uuid = self.request.data.get('song_uuid')
        if not song_uuid:
            raise serializers.ValidationError({'song_uuid': 'This field is required.'})

        song = get_object_or_404(Song, id=song_uuid, user=self.request.user)
        serializer.save(song=song)

    def perform_update(self, serializer):
        # Ensure user can only update their own bubbles
        instance = self.get_object()
        if instance.song.user != self.request.user:
            raise PermissionDenied("You can only edit your own bubbles.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure user can only delete their own bubbles
        if instance.song.user != self.request.user:
            raise PermissionDenied("You can only delete your own bubbles.")
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, subscription_or_trial_permission(require_subscription=True)]

    def get_queryset(self):
        # Filter by song if provided
        song_uuid = self.request.query_params.get('song_uuid')
        if song_uuid:
            return Comment.objects.filter(song__user=self.request.user, song_id=song_uuid)
        return Comment.objects.filter(song__user=self.request.user)

    def perform_create(self, serializer):
        song_uuid = self.request.data.get('song_uuid')
        if not song_uuid:
            raise serializers.ValidationError({'song_uuid': 'This field is required.'})

        song = get_object_or_404(Song, id=song_uuid, user=self.request.user)
        serializer.save(song=song)

    def perform_update(self, serializer):
        # Ensure user can only update their own comments
        instance = self.get_object()
        if instance.song.user != self.request.user:
            raise PermissionDenied("You can only edit your own comments.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure user can only delete their own comments
        if instance.song.user != self.request.user:
            raise PermissionDenied("You can only delete your own comments.")
        instance.delete()