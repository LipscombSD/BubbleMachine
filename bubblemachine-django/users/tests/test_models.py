from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from ..models import User, UserMetadata
import logging

logger = logging.getLogger('app.models')  # Assuming logger is defined in models.py

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email='test@example.com', password='Password123!')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('Password123!'))

    def test_unique_email(self):
        User.objects.create_user(email='test@example.com', password='Password123!')
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email='test@example.com', password='password456')

    def test_soft_delete(self):
        user = User.objects.create_user(email='test@example.com', password='Password123!')
        user.delete()
        self.assertTrue(user.is_deleted)
        self.assertFalse(user.is_active)

    def test_user_manager_excludes_deleted(self):
        user1 = User.objects.create_user(email='user1@example.com', password='Password123!')
        user2 = User.objects.create_user(email='user2@example.com', password='Password123!')
        user2.delete()
        users = User.objects.all()
        self.assertIn(user1, users)
        self.assertNotIn(user2, users)

    # New tests for is_trial_active property
    def test_is_trial_active_superuser(self):
        user = User.objects.create_superuser(email='super@example.com', password='Password123!')
        self.assertTrue(user.is_trial_active)

    def test_is_trial_active_subscribed(self):
        user = User.objects.create_user(email='sub@example.com', password='Password123!')
        user.is_subscribed = True
        user.save()
        self.assertTrue(user.is_trial_active)

    def test_is_trial_active_active_trial(self):
        user = User.objects.create_user(email='trial@example.com', password='Password123!')
        # trial_end_date is set to 30 days from now by default
        self.assertTrue(user.is_trial_active)

    def test_is_trial_active_expired_trial(self):
        user = User.objects.create_user(email='expired@example.com', password='Password123!')
        user.trial_end_date = timezone.now() - timedelta(days=1)
        user.save()
        self.assertFalse(user.is_trial_active)

    def test_create_user_sets_trial_end_date(self):
        user = User.objects.create_user(email='test@example.com', password='Password123!')
        expected_end_date = timezone.now() + timedelta(days=30)
        self.assertAlmostEqual(user.trial_end_date, expected_end_date, delta=timedelta(seconds=1))

class UserMetadataModelTest(TestCase):
    def test_add_metadata(self):
        user = User.objects.create_user(email='test@example.com', password='Password123!')
        metadata = UserMetadata.objects.create(user=user, key='theme', value='dark')
        self.assertEqual(metadata.key, 'theme')
        self.assertEqual(metadata.value, 'dark')

    def test_unique_together(self):
        user = User.objects.create_user(email='test@example.com', password='Password123!')
        UserMetadata.objects.create(user=user, key='theme', value='dark')
        with self.assertRaises(IntegrityError):
            UserMetadata.objects.create(user=user, key='theme', value='light')