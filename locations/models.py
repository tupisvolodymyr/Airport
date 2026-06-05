from django.db import models
from django.core.validators import RegexValidator

class Country(models.Model):
    name = models.CharField(max_length=125, unique=True)
    code = models.CharField(
        max_length=3,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}$',
                message="The country code must consist of exactly 3 capital Latin letters."
            )
        ]
    )

    def clean(self):
        super().clean()
        if self.code:

            self.code = self.code.upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'countries'
        constraints = [
            models.UniqueConstraint(fields=['name', 'code'], name='unique_country_name_and_code')
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class City(models.Model):
    name = models.CharField(max_length=125)
    country = models.ForeignKey(
        'Country', on_delete=models.CASCADE,
        related_name='cities'
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'cities'
        constraints = [
            models.UniqueConstraint(fields=['name', 'country'], name='unique_city_in_country')
        ]

    def __str__(self):
        return f"{self.name}, {self.country.name}"