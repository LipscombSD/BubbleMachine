from rest_framework.test import APITestCase
from bubbles.serializers import BubbleSerializer, CommentSerializer, BubbleSectionSerializer
from bubbles.models import BubbleSection, Bubble, Comment
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()

class BubbleSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='Password123!')
        self.bubble_section = BubbleSection.objects.create(user=self.user)
        self.bubble = Bubble.objects.create(
            bubble_section=self.bubble_section,
            external_id='bubble1',
            layer='1',
            bubble_name='Bubble 1',
            start_time=timedelta(seconds=5.445),
            stop_time=timedelta(seconds=6.784),
            color='#98DDCA'
        )

    def test_serialize_bubble(self):
        serializer = BubbleSerializer(self.bubble)
        data = serializer.data
        self.assertEqual(data['id'], 'bubble1')
        self.assertEqual(data['layer'], '1')
        self.assertEqual(data['bubbleName'], 'Bubble 1')
        self.assertEqual(data['startTime'], '00:05:445')
        self.assertEqual(data['stopTime'], '00:06:784')
        self.assertEqual(data['color'], '#98DDCA')

    def test_deserialize_bubble(self):
        data = {
            'id': 'bubble2',
            'layer': '2',
            'bubbleName': 'Bubble 2',
            'startTime': '00:10:000',
            'stopTime': '00:15:000',
            'color': '#FFFFFF'
        }
        serializer = BubbleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        bubble = serializer.save(bubble_section=self.bubble_section)
        self.assertEqual(bubble.external_id, 'bubble2')
        self.assertEqual(bubble.start_time, timedelta(seconds=10))
        self.assertEqual(bubble.stop_time, timedelta(seconds=15))

    def test_invalid_time_format(self):
        data = {
            'id': 'bubble3',
            'layer': '3',
            'bubbleName': 'Bubble 3',
            'startTime': 'invalid',
            'stopTime': '00:20:000',
            'color': '#000000'
        }
        serializer = BubbleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('startTime', serializer.errors)

class CommentSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='Password123!')
        self.bubble_section = BubbleSection.objects.create(user=self.user)
        self.comment = Comment.objects.create(
            bubble_section=self.bubble_section,
            external_id='comment1',
            start_time=timedelta(seconds=7.478836),
            end_time=timedelta(seconds=9.0361),
            text='Hello'
        )

    def test_serialize_comment(self):
        serializer = CommentSerializer(self.comment)
        data = serializer.data
        self.assertEqual(data['id'], 'comment1')
        self.assertAlmostEqual(float(data['startTime']), 7.478836, places=6)
        self.assertAlmostEqual(float(data['endTime']), 9.0361, places=6)
        self.assertEqual(data['text'], 'Hello')

    def test_deserialize_comment(self):
        data = {
            'id': 'comment2',
            'startTime': 10.0,
            'endTime': 12.0,
            'text': 'New comment'
        }
        serializer = CommentSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        comment = serializer.save(bubble_section=self.bubble_section)
        self.assertEqual(comment.external_id, 'comment2')
        self.assertEqual(comment.start_time, timedelta(seconds=10))
        self.assertEqual(comment.end_time, timedelta(seconds=12))

class BubbleSectionSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='Password123!')

    def test_create_bubble_section(self):
        data = {
            'bubbles': [
                {
                    'id': 'bubble1',
                    'layer': '1',
                    'bubbleName': 'Bubble 1',
                    'startTime': '00:05:445',
                    'stopTime': '00:06:784',
                    'color': '#98DDCA'
                }
            ],
            'comments': [
                {
                    'id': 'comment1',
                    'startTime': 7.478836,
                    'endTime': 9.0361,
                    'text': 'Hello'
                }
            ]
        }
        serializer = BubbleSectionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        bubble_section = serializer.save(user=self.user)
        self.assertEqual(bubble_section.bubbles.count(), 1)
        self.assertEqual(bubble_section.comments.count(), 1)

    def test_update_bubble_section(self):
        bubble_section = BubbleSection.objects.create(user=self.user)
        Bubble.objects.create(
            bubble_section=bubble_section,
            external_id='bubble1',
            layer='1',
            bubble_name='Bubble 1',
            start_time=timedelta(seconds=5),
            stop_time=timedelta(seconds=10),
            color='#FFFFFF'
        )
        Comment.objects.create(
            bubble_section=bubble_section,
            external_id='comment1',
            start_time=timedelta(seconds=7),
            end_time=timedelta(seconds=9),
            text='Hello'
        )

        data = {
            'bubbles': [
                {
                    'id': 'bubble1',
                    'layer': '1',
                    'bubbleName': 'Updated Bubble 1',
                    'startTime': '00:05:000',
                    'stopTime': '00:10:000',
                    'color': '#FFFFFF'
                },
                {
                    'id': 'bubble2',
                    'layer': '2',
                    'bubbleName': 'New Bubble',
                    'startTime': '00:15:000',
                    'stopTime': '00:20:000',
                    'color': '#000000'
                }
            ],
            'comments': [
                {
                    'id': 'comment2',
                    'startTime': 10.0,
                    'endTime': 12.0,
                    'text': 'New Comment'
                }
            ]
        }
        serializer = BubbleSectionSerializer(bubble_section, data=data)
        self.assertTrue(serializer.is_valid())
        updated_section = serializer.save()
        self.assertEqual(updated_section.bubbles.count(), 2)
        self.assertEqual(updated_section.comments.count(), 1)
        with self.assertRaises(Comment.DoesNotExist):
            updated_section.comments.get(external_id='comment1')

    def test_duplicate_bubble_ids(self):
        data = {
            'bubbles': [
                {'id': 'bubble1', 'layer': '1', 'bubbleName': 'Bubble 1', 'startTime': '00:05:000', 'stopTime': '00:10:000', 'color': '#FFFFFF'},
                {'id': 'bubble1', 'layer': '2', 'bubbleName': 'Bubble 2', 'startTime': '00:15:000', 'stopTime': '00:20:000', 'color': '#000000'}
            ],
            'comments': []
        }
        serializer = BubbleSectionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEqual(str(serializer.errors['non_field_errors'][0]), 'Duplicate bubble IDs are not allowed')