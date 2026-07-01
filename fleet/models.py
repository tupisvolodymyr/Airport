from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=125)
    iata_code = models.CharField(
        max_length=3,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{3}$',
                message="IATA the airport code must consist of exactly 3 capital Latin letters (for example, KBP, LWO)."
            )
        ]
    )

    city = models.ForeignKey(
        'locations.city', on_delete=models.PROTECT,
        related_name='airports'
    )

    def clean(self):
        if self.iata_code:
            self.iata_code = self.iata_code.upper()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']

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

    def clean(self):
        super().clean()

        if self.year:
            current_year = timezone.now().year
            if self.year > current_year:
                raise ValidationError({
                    'year': "The release year of the aircraft cannot be in the future."
                })
            if self.year < 1950:
                raise ValidationError({
                    'year': "The year of manufacture cannot be earlier than 1950."
                })

        if self.rows is not None and self.rows <= 0:
            raise ValidationError({
                'rows': "The number of rows must be greater than 0."
            })

        if self.seats_per_row is not None:
            if self.seats_per_row <= 0:
                raise ValidationError({
                    'seats_per_row': "The number of seats in a row must be greater than 0."
                })
            if self.seats_per_row > 12:
                raise ValidationError({
                    'seats_per_row': "The maximum number of seats in one row cannot exceed 12."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.model}) - {self.year}"

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
    seat = models.CharField(max_length=2)

    class ClassType(models.TextChoices):
        BUSINESS = "BUSINESS", "business"
        ECONOMY = "ECONOMY", "economy"

    class_type = models.CharField(
        max_length=10,
        choices=ClassType.choices,
        default=ClassType.ECONOMY
    )

    def clean(self):
        super().clean()
        if self.airplane:
            if self.row > self.airplane.rows:
                raise ValidationError({
                    'row': f"Row number ({self.row}) cannot exceed the number of rows in the plane ({self.airplane.rows})."
                })

            if self.seat:
                seat_letter = self.seat.upper()
                if len(seat_letter) == 1 and 'A' <= seat_letter <= 'Z':
                    seat_index = ord(seat_letter) - 64
                    if seat_index > self.airplane.seats_per_row:
                        raise ValidationError({
                            'seat': f"Seat '{self.seat}' goes beyond the row of this aircraft (maximum seats in the row: {self.airplane.seats_per_row})."
                        })
                else:
                    raise ValidationError({
                        'seat': "The seat number must be a single Latin letter."
                    })

    def save(self, *args, **kwargs):
        if self.seat:
            self.seat = self.seat.upper()
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['airplane', 'row', 'seat'], name='unique_airplane_seat'
            )
        ]

    def __str__(self):
        return f"{self.airplane.name} - Row {self.row}, Seat {self.seat}"


class Airline(models.Model):
    name = models.CharField(max_length=250)
    iata_code = models.CharField(
        max_length=2,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9]{2}$',
                message="IATA The airline code must consist of exactly 2 capital Latin letters or numbers (for example, UA, W6)."
            )
        ]
    )
    founded_year = models.IntegerField()
    airport = models.ManyToManyField(
        'Airport',
        related_name='airlines',
        blank=True,
    )

    def clean(self):
        super().clean()
        if self.iata_code:
            self.iata_code = self.iata_code.upper()
        if self.founded_year:
            current_year = timezone.now().year
            if self.founded_year > current_year:
                raise ValidationError({
                    'founded_year': "Founded year cannot be in the future."
                })
            if self.founded_year < 1900:
                raise ValidationError({
                    'founded_year': "Founded year cannot be earlier than 1900."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name + ' ' + self.iata_code