from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from bubbles.models import BubbleSection
from django.contrib.auth import get_user_model

User = get_user_model()

class BubbleSectionViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.subscribed_user = User.objects.create_user(email='sub@example.com', password='Password123!', is_subscribed=True)
        self.non_subscribed_user = User.objects.create_user(email='nonsub@example.com', password='Password123!', is_subscribed=False)
        self.other_user = User.objects.create_user(email='other@example.com', password='Password123!', is_subscribed=True)

        self.bubble_section1 = BubbleSection.objects.create(user=self.subscribed_user)
        self.bubble_section2 = BubbleSection.objects.create(user=self.other_user)

    def test_list_bubble_sections_subscribed(self):
        self.client.force_authenticate(user=self.subscribed_user)
        url = reverse('bubble-section-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(self.bubble_section1.id))

    def test_list_bubble_sections_non_subscribed(self):
        self.client.force_authenticate(user=self.non_subscribed_user)
        url = reverse('bubble-section-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_bubble_section(self):
        self.client.force_authenticate(user=self.subscribed_user)
        url = reverse('bubble-section-list')
        data = {
            'bubbles': [{'id': 'bubble1', 'layer': '1', 'bubbleName': 'Bubble 1', 'startTime': '00:05:000', 'stopTime': '00:10:000', 'color': '#FFFFFF'}],
            'comments': [{'id': 'comment1', 'startTime': 5.0, 'endTime': 10.0, 'text': 'Test comment'}]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BubbleSection.objects.count(), 3)  # 2 from setUp + 1 new
        new_section = BubbleSection.objects.latest('created_at')
        self.assertEqual(new_section.user, self.subscribed_user)
        self.assertEqual(new_section.bubbles.count(), 1)
        self.assertEqual(new_section.comments.count(), 1)

    def test_retrieve_own_bubble_section(self):
        self.client.force_authenticate(user=self.subscribed_user)
        url = reverse('bubble-section-detail', kwargs={'pk': self.bubble_section1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.bubble_section1.id))

    def test_retrieve_other_user_bubble_section(self):
        self.client.force_authenticate(user=self.subscribed_user)
        url = reverse('bubble-section-detail', kwargs={'pk': self.bubble_section2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_bubble_section(self):
        self.client.force_authenticate(user=self.subscribed_user)
        url = reverse('bubble-section-detail', kwargs={'pk': self.bubble_section1.id})
        data = {
            'bubbles': [{'id': 'bubble1', 'layer': '1', 'bubbleName': 'Updated Bubble', 'startTime': '00:05:000', 'stopTime': '00:10:000', 'color': '#FFFFFF'}],
            'comments': []
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.bubble_section1.refresh_from_db()
        self.assertEqual(self.bubble_section1.bubbles.first().bubble_name, 'Updated Bubble')
        self.assertEqual(self.bubble_section1.comments.count(), 0)

    def test_delete_bubble_section(self):
        self.client.force_authenticate(user=self.subscribed_user)
        url = reverse('bubble-section-detail', kwargs={'pk': self.bubble_section1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BubbleSection.objects.filter(id=self.bubble_section1.id).exists())

    def test_create_with_invalid_data(self):
        self.client.force_authenticate(user=self.subscribed_user)
        url = reverse('bubble-section-list')
        data = {
            'bubbles': [{'id': 'bubble1', 'layer': '1', 'bubbleName': 'Bubble 1', 'startTime': 'invalid', 'stopTime': '00:10:000', 'color': '#FFFFFF'}],
            'comments': []
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('bubbles', response.data)
        self.assertIn('startTime', response.data['bubbles'][0])