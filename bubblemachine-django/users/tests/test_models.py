from django.test import TestCase
from django.db import IntegrityError
from ..models import User, UserMetadata

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