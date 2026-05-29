from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=125)
    code = models.CharField(max_length=3, blank=True)

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=125)
    country = models.ForeignKey(
        'Country', on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name