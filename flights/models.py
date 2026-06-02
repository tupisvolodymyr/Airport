from django.db import models


class FlightStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'scheduled'
    BOARDING = 'BOARDING', 'boarding'
    DEPARTED = 'DEPARTED', 'departed'
    DELAYED = 'DELAYED', 'delayed'
    CANCELLED = 'CANCELLED', 'cancelled'

class BookingStatus(models.TextChoices):
    PENDING = 'PENDING', 'pending'
    CONFIRMED = 'CONFIRMED', 'confirmed'
    CANCELLED = 'CANCELLED', 'cancelled'

class TicketStatus(models.TextChoices):
    BOOKED = 'BOOKED', 'booked'
    USED = 'USED', 'used'
    PAID = 'PAID', 'paid'
    CANCELLED = 'CANCELLED', 'cancelled'


class Flight(models.Model):
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
        decimal_places=2
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

    def __str__(self):
        return f"{self.departure_airport} - {self.arrival_airport}"

class Booking(models.Model):
    user_id = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
    )

    status = models.CharField(
        max_length=10,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Ticket(models.Model):
    flight_number = models.ForeignKey(
        'flights.Flight',
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    booking = models.ForeignKey(
        'flights.Booking',
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    passenger_name = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
    )
    flight_seat = models.OneToOneField(
        'fleet.AirplaneSeat',
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )