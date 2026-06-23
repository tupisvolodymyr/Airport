from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from flights.models import Flight, Booking, Ticket
from flights.permissions import IsOwnerOrAdmin
from flights.serializers import (
    FlightSerializer,
    FlightListSerializer,
    BookingSerializer,
    TicketSerializer,
)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()

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

    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm(self, request, pk=None):
        booking = self.get_object()

        if booking.status != Booking.BookingStatus.PENDING:
            return Response(
                {'detail': f"Booking already has status '{booking.get_status_display()}' and cannot be confirmed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        tickets = booking.tickets.all()
        if not tickets.exists():
            return Response(
                {'detail': "Cannot confirm empty booking. Please add at least one ticket."},
                status=status.HTTP_400_BAD_REQUEST
            )

        total = sum(ticket.price for ticket in tickets)
        tickets.update(status=Ticket.TicketStatus.PAID)

        booking.total_price = total
        booking.status = Booking.BookingStatus.CONFIRMED
        booking.save(update_fields=['total_price', 'status'])

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        booking = self.get_object()

        if booking.status == Booking.BookingStatus.CANCELLED:
            return Response(
                {'detail': "Booking is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

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