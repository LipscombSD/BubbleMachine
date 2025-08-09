from rest_framework import serializers
from .models import Song, Bubble, Comment
from datetime import timedelta


def parse_time_string(time_str):
    parts = time_str.split(':')
    if len(parts) != 3:
        raise ValueError("Invalid time format")
    minutes, seconds, milliseconds = map(int, parts)
    total_seconds = minutes * 60 + seconds + milliseconds / 1000
    return timedelta(seconds=total_seconds)


def format_time_delta(td):
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = round((total_seconds - int(total_seconds)) * 1000)
    return f"{minutes:02d}:{seconds:02d}:{milliseconds:03d}"


class BubbleTimeField(serializers.Field):
    def to_representation(self, value):
        return format_time_delta(value)

    def to_internal_value(self, data):
        try:
            return parse_time_string(data)
        except ValueError:
            raise serializers.ValidationError("Invalid time format. Use MM:SS:MMM")


class CommentTimeField(serializers.Field):
    def to_representation(self, value):
        return value.total_seconds()

    def to_internal_value(self, data):
        try:
            return timedelta(seconds=float(data))
        except ValueError:
            raise serializers.ValidationError("Invalid time value. Use seconds as float")


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'song_hash', 'title', 'artist', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_song_hash(self, value):
        if len(value) != 64:
            raise serializers.ValidationError("Song hash must be 64 characters (SHA-256)")
        return value


class BubbleSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(source='id', read_only=True)  # Internal UUID
    id = serializers.CharField(source='external_id')  # Client-side ID
    startTime = BubbleTimeField(source='start_time')
    stopTime = BubbleTimeField(source='stop_time')
    bubbleName = serializers.CharField(source='bubble_name')
    song_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Bubble
        fields = ['uuid', 'id', 'layer', 'bubbleName', 'startTime', 'stopTime', 'color', 'song_id']

    def validate(self, data):
        # Check for duplicate external_id within the same song
        external_id = data.get('external_id')
        song_id = self.context['request'].data.get('song_id')

        if external_id and song_id:
            # For updates, exclude current instance
            queryset = Bubble.objects.filter(song_id=song_id, external_id=external_id)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError("A bubble with this ID already exists for this song.")

        return data


class CommentSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(source='id', read_only=True)  # Internal UUID
    id = serializers.CharField(source='external_id')  # Client-side ID
    startTime = CommentTimeField(source='start_time')
    endTime = CommentTimeField(source='end_time')
    song_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Comment
        fields = ['uuid', 'id', 'startTime', 'endTime', 'text', 'song_id']

    def validate(self, data):
        # Check for duplicate external_id within the same song
        external_id = data.get('external_id')
        song_id = self.context['request'].data.get('song_id')

        if external_id and song_id:
            # For updates, exclude current instance
            queryset = Comment.objects.filter(song_id=song_id, external_id=external_id)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError("A comment with this ID already exists for this song.")

        return data


class SongDataSerializer(serializers.Serializer):
    """Serializer for saving/retrieving bubbles and comments for a song"""
    song_hash = serializers.CharField(max_length=64)
    bubbles = BubbleSerializer(many=True, required=False, default=list)
    comments = CommentSerializer(many=True, required=False, default=list)

    def validate_song_hash(self, value):
        if len(value) != 64:
            raise serializers.ValidationError("Song hash must be 64 characters (SHA-256)")
        return value

    def validate(self, data):
        bubbles = data.get('bubbles', [])
        comments = data.get('comments', [])

        # Check for duplicate bubble IDs
        if bubbles:
            bubble_ids = [b.get('external_id') for b in bubbles]
            if len(bubble_ids) != len(set(bubble_ids)):
                raise serializers.ValidationError("Duplicate bubble IDs are not allowed")

        # Check for duplicate comment IDs
        if comments:
            comment_ids = [c.get('external_id') for c in comments]
            if len(comment_ids) != len(set(comment_ids)):
                raise serializers.ValidationError("Duplicate comment IDs are not allowed")

        return data

    def create(self, validated_data):
        song_hash = validated_data['song_hash']
        bubbles_data = validated_data.get('bubbles', [])
        comments_data = validated_data.get('comments', [])
        user = self.context['request'].user

        # Get or create the song
        song, created = Song.objects.get_or_create(
            song_hash=song_hash,
            defaults={'user': user}
        )

        # Clear existing bubbles and comments for this song
        song.bubbles.all().delete()
        song.comments.all().delete()

        # Create new bubbles
        for bubble_data in bubbles_data:
            Bubble.objects.create(song=song, **bubble_data)

        # Create new comments
        for comment_data in comments_data:
            Comment.objects.create(song=song, **comment_data)

        return {
            'song': song,
            'bubbles': song.bubbles.all(),
            'comments': song.comments.all()
        }


class SongWithDataSerializer(serializers.ModelSerializer):
    """Serializer for retrieving a song with its bubbles and comments"""
    bubbles = BubbleSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Song
        fields = ['id', 'song_hash', 'title', 'artist', 'created_at', 'updated_at', 'bubbles', 'comments']