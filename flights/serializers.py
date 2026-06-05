from django.core.exceptions import ValidationError
from rest_framework import serializers
from flights.models import Flight, Booking, Ticket
from fleet.serializers import AirportSerializer, AirplaneSerializer, AirlineSerializer


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            'id', 'flight_number', 'departure_airport', 'departure_time',
            'arrival_airport', 'arrival_time', 'ticket_price', 'airplane',
            'airline', 'flight_status', 'created_at'
        ]

    def validate(self, attrs):
        instance = Flight(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'status', 'total_price', 'created_at'
        ]

    def validate(self, attrs):
        instance = Booking(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'flight', 'booking', 'user', 'price', 'flight_seat'
        ]

    def validate(self, attrs):
        instance = Ticket(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs


class FlightListSerializer(FlightSerializer):
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    airline = AirlineSerializer(read_only=True)