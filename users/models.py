from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'Admin', 'admin'
        USER = 'User', 'user'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=15, choices=Roles.choices, default=Roles.USER
    )

    phone = models.CharField(max_length=15, blank=True, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} - {self.role}"