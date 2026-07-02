from django.urls import path, include
from rest_framework.routers import DefaultRouter
from flights.views import (
    FlightViewSet,
    BookingViewSet,
    TicketViewSet,
    StripeWebhookView,
    PaymentSuccessView,
    PaymentCancelView,
)


router = DefaultRouter()
router.register('flights', FlightViewSet, basename='flight')
router.register('tickets', TicketViewSet, basename='ticket')
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('payments/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payments/cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
]