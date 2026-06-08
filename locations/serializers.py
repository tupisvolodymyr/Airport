from django.core.exceptions import ValidationError
from rest_framework import serializers
from locations.models import City, Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

    def validate(self, attrs):
        instance = Country(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

    def validate(self, attrs):
        instance = City(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return attrs