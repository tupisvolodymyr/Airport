from django.urls import path, include
from rest_framework.routers import DefaultRouter
from flights.views import FlightViewSet, BookingViewSet, TicketViewSet


router = DefaultRouter()
router.register('flights', FlightViewSet, basename='flight')
router.register('tickets', TicketViewSet, basename='ticket')
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
]