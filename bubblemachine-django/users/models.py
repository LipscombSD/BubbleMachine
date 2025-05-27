import uuid
import logging
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager

logger = logging.getLogger(__name__)

class User(AbstractBaseUser, PermissionsMixin):
    """User"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'

    def __str__(self):
        return self.email

    def delete(self, using=None, keep_parents=False):
        """Soft delete"""
        self.is_deleted = True
        self.is_active = False
        self.save(using=using)
        logger.info(f"User {self.email} soft deleted")

    def hard_delete(self, using=None, keep_parents=False):
        """Hard delete from database"""
        super().delete(using=using, keep_parents=keep_parents)

class UserMetadata(models.Model):
    """Key-value store for user metadata"""
    # I don't like having to add columns to the User table if I don't have to.
    # This is an easy way to avoid that.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metadata')
    key = models.CharField(max_length=100)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'key']
        indexes = [
            models.Index(fields=['user', 'key']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.key}: {self.value}"