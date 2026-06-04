from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=125, unique=True)
    code = models.CharField(max_length=3)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'countries'


    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=125)
    country = models.ForeignKey(
        'Country', on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'cities'

    def __str__(self):
        return self.name