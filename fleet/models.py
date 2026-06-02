from django.db import models

class Airport(models.Model):
    name = models.CharField(max_length=125)
    iata_code = models.CharField(max_length=3, unique=True)

    city = models.ForeignKey(
        'locations.city', on_delete=models.PROTECT,
        related_name='airports'
    )

    class Meta:
        ordering = ['name' ]

    def __str__(self):
        return self.name + ' ' + self.iata_code

class Airplane(models.Model):
    name = models.CharField(max_length=125)
    model = models.CharField(max_length=125)
    year = models.IntegerField()

    rows = models.PositiveIntegerField()
    seats_per_row = models.PositiveIntegerField()

    airline = models.ForeignKey(
        'Airline',
        on_delete=models.CASCADE,
        related_name='airplanes',

    )

    def __str__(self):
        return self.name + ' ' + self.model + ' ' + self.year

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Airplanes"

class AirplaneSeat(models.Model):
    airplane = models.ForeignKey(
        'Airplane',
        on_delete=models.CASCADE,
        related_name='seats',
    )
    row = models.PositiveIntegerField()
    seat = models.CharField()

    class ClassType(models.TextChoices):
        BUSINESS = "BUSINESS", "business"
        ECONOMY = "ECONOMY", "economy"

    class_type = models.CharField(
        max_length=10,
        choices=ClassType.choices,
        default=ClassType.ECONOMY
    )


class Airline(models.Model):
    name = models.CharField(max_length=250)
    iata_code = models.CharField(max_length=2, unique=True)
    created_at = models.IntegerField(blank=False, null=False)

    airport = models.ManyToManyField(
        'Airport',
        related_name='airlines',
        blank=True,
    )

    def __str__(self):
        return self.name + ' ' + self.iata_code