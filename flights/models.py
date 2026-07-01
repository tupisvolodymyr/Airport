from django.core.validators import MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Flight(models.Model):
    class FlightStatus(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'scheduled'
        BOARDING = 'BOARDING', 'boarding'
        DEPARTED = 'DEPARTED', 'departed'
        DELAYED = 'DELAYED', 'delayed'
        CANCELLED = 'CANCELLED', 'cancelled'

    flight_number = models.CharField(max_length=10)
    departure_airport = models.ForeignKey(
        'fleet.Airport', on_delete=models.PROTECT,
        related_name='departures'
    )
    departure_time = models.DateTimeField()
    arrival_airport = models.ForeignKey(
        'fleet.Airport', on_delete=models.PROTECT,
        related_name='arrivals'
    )
    arrival_time = models.DateTimeField()

    ticket_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message="Flight ticket price must be greater than 0.")]
    )
    airplane = models.ForeignKey(
        'fleet.Airplane', on_delete=models.PROTECT
    )
    airline = models.ForeignKey(
        'fleet.Airline', on_delete=models.PROTECT
    )
    flight_status = models.CharField(
        max_length=10,
        choices=FlightStatus.choices,
        default=FlightStatus.SCHEDULED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.departure_time and self.arrival_time:
            if self.departure_time >= self.arrival_time:
                raise ValidationError({
                    'arrival_time': "Arrival time must be later than departure time."
                })
            if self.departure_time < timezone.now():
                raise ValidationError({
                    'departure_time': "Departure time cannot be in the past. Please enter a current date."
                })
            if self.arrival_airport == self.departure_airport:
                raise ValidationError({
                    'arrival_airport': "Arrival airport cannot be the same as departure airport."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.flight_number}: {self.departure_airport.iata_code} -> {self.arrival_airport.iata_code}"





class Booking(models.Model):
    class BookingStatus(models.TextChoices):
        PENDING = 'PENDING', 'pending'
        CONFIRMED = 'CONFIRMED', 'confirmed'
        CANCELLED = 'CANCELLED', 'cancelled'

    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name='bookings'
    )
    status = models.CharField(
        max_length=10,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} by {self.user.username} ({self.status})"


class Ticket(models.Model):
    class TicketStatus(models.TextChoices):
        BOOKED = 'BOOKED', 'booked'
        USED = 'USED', 'used'
        PAID = 'PAID', 'paid'
        CANCELLED = 'CANCELLED', 'cancelled'

    flight = models.ForeignKey(
        'flights.Flight',
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    booking = models.ForeignKey(
        'flights.Booking',
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    flight_seat = models.ForeignKey(
        'fleet.AirplaneSeat',
        on_delete=models.PROTECT,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message="Ticket price must be greater than 0.")]
    )

    def clean(self):
        super().clean()
        if self.flight and self.flight_seat:
            if self.flight.airplane != self.flight_seat.airplane:
                raise ValidationError({
                    'flight_seat': f"The selected seat does not belong to the plane ({self.flight.airplane.name}), who operates this flight"
                })

            duplicate_tickets = Ticket.objects.filter(
                flight=self.flight,
                flight_seat=self.flight_seat
            )
            if self.pk:
                duplicate_tickets = duplicate_tickets.exclude(pk=self.pk)

            if duplicate_tickets.exists():
                raise ValidationError({
                    'flight_seat': "This seat on the selected flight is already booked.."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['flight', 'flight_seat'], name='unique_flight_seat')
        ]
        ordering = ['id']

    def __str__(self):
        return f"Ticket {self.id} for Flight {self.flight.flight_number} (Seat {self.flight_seat.row}{self.flight_seat.seat})"


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING   = 'PENDING',   'pending'
        SUCCEEDED = 'SUCCEEDED', 'succeeded'
        FAILED    = 'FAILED',    'failed'

    booking = models.OneToOneField(
        'flights.Booking',
        on_delete=models.CASCADE,
        related_name='payment'
    )
    stripe_session_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id} ({self.status})"