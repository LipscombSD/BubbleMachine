from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from datetime import timedelta

class UserManager(BaseUserManager):
    """Custom user manager"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Set trial_end_date during model initialization
        extra_fields['trial_end_date'] = timezone.now() + timedelta(days=30)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(email, password, **extra_fields)
        return user

    def get_queryset(self):
        """Exclude soft-deleted users by default"""
        return super().get_queryset().filter(is_deleted=False)