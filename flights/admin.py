from django.contrib import admin

from flights.models import Flight, Booking, Ticket

admin.site.register(Flight)
admin.site.register(Booking)
admin.site.register(Ticket)
