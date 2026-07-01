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


class FlightListSerializer(FlightSerializer):
    departure_airport = AirportSerializer(read_only=True)
    arrival_airport = AirportSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    airline = AirlineSerializer(read_only=True)


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user_id', 'status', 'total_price', 'created_at']
        read_only_fields = ['user_id', 'status', 'total_price', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'flight', 'flight_seat', 'booking', 'user', 'price']
        read_only_fields = ['booking', 'user', 'price']


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'flight', 'flight_seat']

    def create(self, validated_data):
        booking = self.context['booking']
        user = self.context['request'].user
        flight = validated_data['flight']

        ticket = Ticket.objects.create(
            flight=flight,
            flight_seat=validated_data['flight_seat'],
            booking=booking,
            user=user,
            price=flight.ticket_price,
        )
        return ticket