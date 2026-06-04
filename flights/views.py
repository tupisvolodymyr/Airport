from django.shortcuts import render
from rest_framework import viewsets
from flights.models import Flight, Booking, Ticket
from flights.serializers import FlightSerializer, BookingSerializer, TicketSerializer, FlightSerializer, FlightListSerializer



class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return FlightListSerializer
        return FlightSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


