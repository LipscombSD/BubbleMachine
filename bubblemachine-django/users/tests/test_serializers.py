from django.test import TestCase
from ..serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
from ..models import User

class UserRegistrationSerializerTest(TestCase):
    def test_valid_data(self):
        data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'test@example.com')

    def test_password_mismatch(self):
        data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'password_confirm': 'DifferentPassword123!',
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class UserLoginSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='Password123!')

    def test_valid_credentials(self):
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_invalid_credentials(self):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class UserProfileSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@example.com', password='Password123!')

    def test_serialize_user(self):
        serializer = UserProfileSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['email'], 'test@example.com')
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)