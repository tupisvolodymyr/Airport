from rest_framework import serializers
from fleet.models import Airport, Airline, Airplane, AirplaneSeat
from django.core.exceptions import ValidationError


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'

    def validate(self, attrs):
        instance = Airport(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs



class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = '__all__'

    def validate(self, attrs):
        instance = Airline(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = '__all__'

    def validate(self, attrs):
        instance = Airplane(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs


class AirplaneSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneSeat
        fields = '__all__'

    def validate(self, attrs):
        instance = AirplaneSeat(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs