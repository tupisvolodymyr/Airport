from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'Admin', 'admin'
        USER = 'User', 'user'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=15, choices=Roles.choices, default=Roles.USER
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+\d{1,14}$',
                message="The phone number must be in international format (for example, +380991234567)."
            )
        ]
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def clean(self):
        if self.phone == '':
            self.phone = None
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} - {self.role}"