import logging
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from users.models import User

logger = logging.getLogger(__name__)

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    stripe_subscription_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'stripe_subscription_id']

    def __str__(self):
        return f"{self.user.email} - {self.stripe_subscription_id} ({self.status})"