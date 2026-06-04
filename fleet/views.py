from django.shortcuts import render
from rest_framework import viewsets
from fleet.models import Airport, Airplane, AirplaneSeat, Airline
from fleet.serializers import (AirportSerializer, AirplaneSerializer, AirplaneSeatSerializer, AirlineSerializer)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer


class AirplaneSeatViewSet(viewsets.ModelViewSet):
    queryset = AirplaneSeat.objects.all()
    serializer_class = AirplaneSeatSerializer


class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer