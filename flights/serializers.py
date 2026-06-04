from rest_framework import serializers
from flights.models import Flight, Booking, Ticket
from fleet.serializers import *


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'departure_airport', 'departure_time',
            'arrival_airport', 'arrival_time', 'ticket_price', 'airplane',
            'airline', 'flight_status', 'created_at'
        ]

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'user_id', 'status', 'total_price', 'created_at'
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'flight_number', 'booking', 'passenger_name', 'price',
            'flight_seat'
        ]


class FlightListSerializer(FlightSerializer):
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    airline = AirlineSerializer(read_only=True)