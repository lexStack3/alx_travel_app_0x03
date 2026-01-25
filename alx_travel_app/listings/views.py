import uuid
import requests

from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Listing, Booking, Review, Payment
from .serializers import (
    ListingSerializer,
    BookingSerializer,
    ReviewSerializer
)
from .tasks import (
    send_payment_confirmation_email,
    send_booking_confirmation_email
)


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all().select_related('operator')
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        booking = serializer.save()

        send_booking_confirmation_email.delay(
            booking.passenger_email,
            str(booking.booking_id)
        )


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

CHAPA_INIT_URL = "https://api.chapa.co/v1/transaction/initialize"
CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify/"


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def initiate_payment(request, booking_id):
    """
    Initiate Chapa payment for a booking.
    """
    booking = get_object_or_404(Booking, booking_id=booking_id)

    if booking.status != "pending":
        return Response(
            {"error": "Payment already processed for this booking"},
            status=status.HTTP_400_BAD_REQUEST
        )

    tx_ref = f"tx-{uuid.uuid4()}"

    payment = Payment.objects.create(
        booking=booking,
        tx_ref=tx_ref,
        amount=booking.amount_paid,
        status="pending"
    )

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    callback_url = request.build_absolute_uri(
        reverse('payment-verify')
    )
    return_url = request.build_absolute_uri(
        reverse('payment-success')
    )

    payload = {
        "amount": str(booking.amount_paid),
        "currency": "ETB",
        "email": booking.passenger_email,
        "first_name": booking.passenger_name,
        "tx_ref": tx_ref,
        "callback_url": callback_url,
        "return_url": return_url,
        "customization": {
            "title": "Travel Booking Payment",
            "description": "Payment for travel booking"
        }
    }

    response = requests.post(
        CHAPA_INIT_URL,
        json=payload,
        headers=headers
    )
    data = response.json()

    if response.status_code == 200 and data.get("status") == "success":
        return Response(
            {
                "checkout_url": data["data"]["checkout_url"],
                "tx_ref": tx_ref
            },
            status=status.HTTP_200_OK
        )

    payment.status = "failed"
    payment.save()

    return Response(
        {"error": "Failed to initiate payment"},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_payment(request):
    """
    Verify Chapa payment after completion.
    """
    tx_ref = request.query_params.get("tx_ref")

    if not tx_ref:
        return Response(
            {"error": "tx_ref is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    payment = get_object_or_404(Payment, tx_ref=tx_ref)

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.get(
        f"{CHAPA_VERIFY_URL}{tx_ref}",
        headers=headers
    )

    data = response.json()

    if response.status_code == 200 and data.get("status") == "success":
        if data["data"]["status"] == "success":
            payment.status = "completed"
            payment.chapa_transaction_id = data["data"]["id"]
            payment.save()

            booking = payment.booking
            booking.status = "confirmed"
            booking.save()

            send_payment_confirmation_email.delay(
                booking.passenger_email,
                str(booking.booking_id),
                str(payment.amount)
            )

            return Response(
                {"message": "Payment verified successfully"},
                status=status.HTTP_200_OK
            )

    payment.status = "failed"
    payment.save()

    return Response(
        {"error": "Payment verification failed"},
        status=status.HTTP_400_BAD_REQUEST
    )
