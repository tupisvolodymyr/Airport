import stripe
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from flights.models import Flight, Booking, Ticket, Payment
from flights.permissions import IsOwnerOrAdmin
from flights.serializers import (
    FlightSerializer,
    FlightListSerializer,
    BookingSerializer,
    TicketSerializer,
    PaymentSerializer,
)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        'departure_airport', 'arrival_airport', 'airplane', 'airline'
    )

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return FlightListSerializer
        return FlightSerializer


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'Admin':
            return Booking.objects.prefetch_related('tickets').all()
        return Booking.objects.prefetch_related('tickets').filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get', 'post'], url_path='tickets')
    def tickets(self, request, pk=None):
        booking = self.get_object()

        if request.method == 'GET':
            serializer = TicketSerializer(booking.tickets.all(), many=True)
            return Response(serializer.data)

        if booking.status != Booking.BookingStatus.PENDING:
            return Response(
                {'detail': f"Cannot add ticket to booking with status '{booking.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            booking=booking,
            user=request.user,
            price=serializer.validated_data['flight'].ticket_price
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'tickets/(?P<ticket_id>\d+)')
    def remove_ticket(self, request, pk=None, ticket_id=None):
        booking = self.get_object()

        if booking.status != Booking.BookingStatus.PENDING:
            return Response(
                {'detail': f"Cannot remove ticket from booking with status '{booking.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket = get_object_or_404(Ticket, pk=ticket_id, booking=booking)
        ticket.delete()

        return Response({'detail': "Ticket successfully removed."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='checkout')
    def checkout(self, request, pk=None):
        booking = self.get_object()

        if booking.status != Booking.BookingStatus.PENDING:
            return Response(
                {'detail': f"Cannot checkout booking with status '{booking.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        tickets = booking.tickets.all()
        if not tickets.exists():
            return Response(
                {'detail': "Cannot checkout empty booking. Please add at least one ticket."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if hasattr(booking, 'payment'):
            if booking.payment.status == Payment.PaymentStatus.SUCCEEDED:
                return Response(
                    {'detail': "This booking has already been paid."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Сесія ще не оплачена або протухла — видаляємо і створюємо нову
            booking.payment.delete()

        total = sum(ticket.price for ticket in tickets)
        amount_cents = int(total * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': settings.STRIPE_CURRENCY,
                    'unit_amount': amount_cents,
                    'product_data': {
                        'name': f"Booking #{booking.id}",
                        'description': f"{tickets.count()} ticket(s) for your flight(s)",
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/api/payments/success/'),
            cancel_url=request.build_absolute_uri('/api/payments/cancel/'),
            metadata={'booking_id': booking.id},
        )

        payment = Payment.objects.create(
            booking=booking,
            stripe_session_id=session.id,
            amount=total,
            currency=settings.STRIPE_CURRENCY,
            status=Payment.PaymentStatus.PENDING,
        )

        return Response({
            'checkout_url': session.url,
            'payment': PaymentSerializer(payment).data,
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status == Booking.BookingStatus.CANCELLED:
            return Response(
                {'detail': "Booking is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.status == Booking.BookingStatus.CONFIRMED:
            return Response(
                {'detail': "Cannot cancel a confirmed booking. Please contact support for refunds."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            booking.tickets.update(status=Ticket.TicketStatus.CANCELLED)
            booking.status = Booking.BookingStatus.CANCELLED
            booking.save(update_fields=['status'])

        return Response({'detail': "Booking and all tickets successfully cancelled."}, status=status.HTTP_200_OK)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = TicketSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'Admin':
            return Ticket.objects.select_related('flight', 'flight_seat').all()
        return Ticket.objects.select_related('flight', 'flight_seat').filter(user=user)


class StripeWebhookView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response({'detail': 'Invalid payload.'}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({'detail': 'Invalid signature.'}, status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_successful_payment(session)

        elif event['type'] == 'checkout.session.expired':
            session = event['data']['object']
            Payment.objects.filter(
                stripe_session_id=session['id']
            ).update(status=Payment.PaymentStatus.FAILED)

        return Response({'detail': 'ok'}, status=status.HTTP_200_OK)

    def _handle_successful_payment(self, session):
        try:
            payment = Payment.objects.select_related('booking').get(
                stripe_session_id=session['id']
            )
        except Payment.DoesNotExist:
            return

        if payment.status == Payment.PaymentStatus.SUCCEEDED:
            return

        with transaction.atomic():
            payment.status = Payment.PaymentStatus.SUCCEEDED
            payment.save(update_fields=['status'])

            booking = payment.booking
            tickets = booking.tickets.all()
            total = sum(ticket.price for ticket in tickets)

            tickets.update(status=Ticket.TicketStatus.PAID)

            booking.total_price = total
            booking.status = Booking.BookingStatus.CONFIRMED
            booking.save(update_fields=['total_price', 'status'])


class PaymentSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {'detail': 'Payment successful. Your booking is confirmed.'},
            status=status.HTTP_200_OK
        )


class PaymentCancelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {'detail': 'Payment cancelled. Your booking is still pending.'},
            status=status.HTTP_200_OK
        )