from django.contrib.auth.models import AbstractUser
from django.db import models

from custom_auth.managers import CustomUserManager


class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    name = models.CharField("name", max_length=50, default="user")
    email = models.EmailField("email address", unique=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    is_password_set = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()



    def __str__(self):
        return self.email
