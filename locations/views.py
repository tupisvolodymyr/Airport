from django.shortcuts import render
from rest_framework import viewsets
from locations.models import City, Country
from locations.serializers import CitySerializer, CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer