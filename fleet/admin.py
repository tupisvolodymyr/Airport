from django.contrib import admin
from fleet.models import Airline, Airport, Airplane, AirplaneSeat

admin.site.register(Airline)
admin.site.register(Airport)
admin.site.register(Airplane)
admin.site.register(AirplaneSeat)
