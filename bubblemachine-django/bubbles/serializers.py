from rest_framework import serializers
from .models import BubbleSection, Bubble, Comment
from datetime import timedelta
from django.db import models


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


class BubbleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='external_id')
    startTime = BubbleTimeField(source='start_time')
    stopTime = BubbleTimeField(source='stop_time')
    bubbleName = serializers.CharField(source='bubble_name')

    class Meta:
        model = Bubble
        fields = ['id', 'layer', 'bubbleName', 'startTime', 'stopTime', 'color']


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='external_id')
    startTime = CommentTimeField(source='start_time')
    endTime = CommentTimeField(source='end_time')

    class Meta:
        model = Comment
        fields = ['id', 'startTime', 'endTime', 'text']


class BubbleSectionSerializer(serializers.ModelSerializer):
    bubbles = BubbleSerializer(many=True, required=False)
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = BubbleSection
        fields = ['id', 'bubbles', 'comments']

    def create(self, validated_data):
        bubbles_data = validated_data.pop('bubbles', [])
        comments_data = validated_data.pop('comments', [])
        bubble_section = BubbleSection.objects.create(**validated_data)
        for bubble_data in bubbles_data:
            Bubble.objects.create(bubble_section=bubble_section, **bubble_data)
        for comment_data in comments_data:
            Comment.objects.create(bubble_section=bubble_section, **comment_data)
        return bubble_section

    def update(self, instance, validated_data):
        # Only process bubbles if they're included in the request
        if 'bubbles' in validated_data:
            bubbles_data = validated_data.pop('bubbles')
            self._update_bubbles(instance, bubbles_data)

        # Only process comments if they're included in the request
        if 'comments' in validated_data:
            comments_data = validated_data.pop('comments')
            self._update_comments(instance, comments_data)

        # Update any other fields on the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def _update_bubbles(self, instance, bubbles_data):
        existing_bubbles = {b.external_id: b for b in instance.bubbles.all()}
        data_bubble_ids = set()

        for bubble_data in bubbles_data:
            external_id = bubble_data.get('external_id')
            if not external_id:
                raise serializers.ValidationError("Each bubble must have an 'id' field")

            data_bubble_ids.add(external_id)
            if external_id in existing_bubbles:
                bubble = existing_bubbles[external_id]
                for key, value in bubble_data.items():
                    if key != 'external_id':  # Don't allow ID changes
                        setattr(bubble, key, value)
                bubble.save()
            else:
                Bubble.objects.create(bubble_section=instance, **bubble_data)

        # Delete bubbles that are no longer in the data
        for external_id in existing_bubbles:
            if external_id not in data_bubble_ids:
                existing_bubbles[external_id].delete()

    def _update_comments(self, instance, comments_data):
        existing_comments = {c.external_id: c for c in instance.comments.all()}
        data_comment_ids = set()

        for comment_data in comments_data:
            external_id = comment_data.get('external_id')
            if not external_id:
                raise serializers.ValidationError("Each comment must have an 'id' field")

            data_comment_ids.add(external_id)
            if external_id in existing_comments:
                comment = existing_comments[external_id]
                for key, value in comment_data.items():
                    if key != 'external_id':  # Don't allow ID changes
                        setattr(comment, key, value)
                comment.save()
            else:
                Comment.objects.create(bubble_section=instance, **comment_data)

        # Delete comments that are no longer in the data
        for external_id in existing_comments:
            if external_id not in data_comment_ids:
                existing_comments[external_id].delete()

    def validate(self, data):
        bubbles = data.get('bubbles', [])
        comments = data.get('comments', [])

        if bubbles:
            bubble_ids = [b.get('external_id') for b in bubbles]
            if len(bubble_ids) != len(set(bubble_ids)):
                raise serializers.ValidationError("Duplicate bubble IDs are not allowed")

        if comments:
            comment_ids = [c.get('external_id') for c in comments]
            if len(comment_ids) != len(set(comment_ids)):
                raise serializers.ValidationError("Duplicate comment IDs are not allowed")

        return data