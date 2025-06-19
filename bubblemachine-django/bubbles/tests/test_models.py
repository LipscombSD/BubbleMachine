from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from bubbles.models import BubbleSection, Bubble, Comment
from datetime import timedelta

User = get_user_model()

class BubbleSectionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='Password123!')

    def test_create_bubble_section(self):
        bubble_section = BubbleSection.objects.create(user=self.user)
        self.assertEqual(bubble_section.user, self.user)
        self.assertIsNotNone(bubble_section.created_at)
        self.assertIsNotNone(bubble_section.updated_at)
        self.assertEqual(str(bubble_section), f"BubbleSection {bubble_section.id} for user {self.user.email}")

class BubbleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='Password123!')
        self.bubble_section = BubbleSection.objects.create(user=self.user)

    def test_create_bubble(self):
        bubble = Bubble.objects.create(
            bubble_section=self.bubble_section,
            external_id='bubble1',
            layer='1',
            bubble_name='Bubble 1',
            start_time=timedelta(seconds=5),
            stop_time=timedelta(seconds=10),
            color='#FFFFFF'
        )
        self.assertEqual(bubble.bubble_section, self.bubble_section)
        self.assertEqual(bubble.external_id, 'bubble1')
        self.assertEqual(str(bubble), f"Bubble {bubble.external_id} in {self.bubble_section}")

    def test_unique_together_constraint(self):
        Bubble.objects.create(
            bubble_section=self.bubble_section,
            external_id='bubble1',
            layer='1',
            bubble_name='Bubble 1',
            start_time=timedelta(seconds=5),
            stop_time=timedelta(seconds=10),
            color='#FFFFFF'
        )
        with self.assertRaises(IntegrityError):
            Bubble.objects.create(
                bubble_section=self.bubble_section,
                external_id='bubble1',
                layer='2',
                bubble_name='Bubble 2',
                start_time=timedelta(seconds=15),
                stop_time=timedelta(seconds=20),
                color='#000000'
            )

class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='Password123!')
        self.bubble_section = BubbleSection.objects.create(user=self.user)

    def test_create_comment(self):
        comment = Comment.objects.create(
            bubble_section=self.bubble_section,
            external_id='comment1',
            start_time=timedelta(seconds=7),
            end_time=timedelta(seconds=9),
            text='Hello'
        )
        self.assertEqual(comment.bubble_section, self.bubble_section)
        self.assertEqual(comment.external_id, 'comment1')
        self.assertEqual(str(comment), f"Comment {comment.external_id} in {self.bubble_section}")

    def test_unique_together_constraint(self):
        Comment.objects.create(
            bubble_section=self.bubble_section,
            external_id='comment1',
            start_time=timedelta(seconds=7),
            end_time=timedelta(seconds=9),
            text='Hello'
        )
        with self.assertRaises(IntegrityError):
            Comment.objects.create(
                bubble_section=self.bubble_section,
                external_id='comment1',
                start_time=timedelta(seconds=10),
                end_time=timedelta(seconds=12),
                text='Another comment'
            )