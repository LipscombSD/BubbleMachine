from rest_framework.test import APITestCase
from rest_framework import status
from ..models import User

class UserViewSetTest(APITestCase):
    def test_register(self):
        url = '/api/v1/users/register/'
        data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
        self.assertIn('user', response.data)

    def test_login(self):
        user = User.objects.create_user(email='test@example.com', password='Password123!')
        url = '/api/v1/users/login/'
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_profile(self):
        user = User.objects.create_user(email='test@example.com', password='Password123!')
        self.client.force_authenticate(user=user)
        url = '/api/v1/users/profile/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_update_profile(self):
        user = User.objects.create_user(email='test@example.com', password='Password123!')
        self.client.force_authenticate(user=user)
        url = '/api/v1/users/update_profile/'
        data = {
            'first_name': 'Updated'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_token_refresh(self):
        register_data = {
            'email': 'test@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
        }
        response = self.client.post('/api/v1/users/register/', register_data, format='json')
        original_tokens = response.data
        refresh_data = {
            'refresh_token': original_tokens['refresh_token']
        }
        response = self.client.post('/api/v1/users/login/refresh/', refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_tokens = response.data
        self.assertNotEqual(new_tokens['access_token'], original_tokens['access_token'])
        self.assertEqual(new_tokens['refresh_token'], original_tokens['refresh_token'])