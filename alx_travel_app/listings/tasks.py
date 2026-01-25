from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 5})
def send_payment_confirmation_email(self, email, booking_id, amount):
    subject = "Payment Confirmation - Travel Booking"
    message = (
        f"Dear Customer,\n\n"
        f"Your payment was successful.\n\n"
        f"Booking ID: {booking_id}\n"
        f"Amount Paid: {amount}\n\n"
        f"Thank you for booking with us."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )

    return "Email Sent ✅"

@shared_task
def send_booking_confirmation_email(passenger_email, booking_id):
    subject = "Booking Created Successfully"
    message = (
        f"Your booking with ID {booking_id} has been created successfully."
        f"You will receive another email once payment is confirmed."
    )

    send_email(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [passenger_email],
        fail_silently=False
    )

    return "Email Sent ✅"
