from rest_framework import serializers
from fleet.models import Airport, Airline, Airplane, AirplaneSeat


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'


class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = '__all__'


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = '__all__'


class AirplaneSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneSeat
        fields = '__all__'