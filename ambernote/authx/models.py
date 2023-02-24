from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model with email as username and more fields
    """

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname']

    # Remove some fields
    username = None  # type: ignore
    first_name = None  # type: ignore
    last_name = None  # type: ignore

    # Add/Override some fields
    uuid = models.UUIDField(unique=True, editable=False, default=uuid4)
    # Use fullname replace first_name and last_name
    fullname = models.CharField(_("full name"), max_length=150)
    email = models.EmailField(_("email address"), unique=True)

    extras = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_full_name(self):
        """Override AbstractUser.get_full_name()"""
        return self.fullname

    def get_short_name(self):
        """Override AbstractUser.get_short_name()"""
        return self.fullname
