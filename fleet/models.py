from django.db import models

class Airport(models.Model):
    name = models.CharField(max_length=125)
    iata_code = models.CharField(max_length=3, unique=True)

    city = models.ForeignKey(
        'locations.city', on_delete=models.PROTECT,
        related_name='airports'
    )

    def __str__(self):
        return self.name + ' ' + self.iata_code

class Airplane(models.Model):
    name = models.CharField(max_length=125)
    model = models.CharField(max_length=125)
    year = models.IntegerField()

    rows = models.IntegerField()
    seats_per_row = models.IntegerField()

    airline = models.ForeignKey(
        'Airline', on_delete=models.PROTECT
    )

    def __str__(self):
        return self.name + ' ' + self.model + ' ' + self.year


class Airline(models.Model):
    name = models.CharField(max_length=250)
    iata_code = models.CharField(max_length=2, unique=True)
    created_at = models.IntegerField(blank=False, null=False)

    base_airport = models.ForeignKey(
        'Airport', on_delete=models.PROTECT,
    )