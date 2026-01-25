import uuid
import pycountry
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


TRANSPORT_CHOICES = (
    ('bus', 'Bus'),
    ('flight', 'Flight'),
    ('train', 'Train'),
    ('boat', 'Boat')
)

LISTING_STATUS = (
    ('active', 'Active'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
)

BOOKING_STATUS = (
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled')
)

STATES = tuple((state.code, state.name) for state in
               pycountry.subdivisions.get(country_code='NG'))


class User(AbstractUser):
    """Custom model representation of a <User> instance."""
    user_id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        indexes = [
            models.Index(fields=['email'])
        ]
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email')
        ]

    def __str__(self):
        """String representation of a <User> instance."""
        return self.username



class Listing(models.Model):
    """Model representation of a <Listing> instance."""
    listing_id = models.UUIDField(primary_key=True,
                                  default=uuid.uuid4, editable=False)
    operator = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='listings')
    transport_type = models.CharField(max_length=30,
                                      choices=TRANSPORT_CHOICES, default='bus')
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(max_length=2048)
    origin = models.CharField(max_length=50, choices=STATES,
                              default='NG-LA', blank=False)
    destination = models.CharField(max_length=50, choices=STATES,
                                   default='NG-CR', blank=False)
    departure_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveIntegerField()
    total_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=50, choices=LISTING_STATUS,
                              default='active', blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of a <Listing> instance."""
        return "{} - {}: ({}) - [{}]".format(self.origin, self.destination,
                                         self.transport_type, self.status)


class Booking(models.Model):
    """Model representation of a <Booking> instance."""
    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                  editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
                                related_name='bookings')
    passenger_name = models.CharField(max_length=128, blank=False)
    passenger_email = models.EmailField(max_length=254, blank=False)
    num_seats = models.PositiveIntegerField()
    booking_date = models.DateTimeField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=BOOKING_STATUS,
                              default='pending', blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('listing', 'passenger_name', 'passenger_email')

    def __str__(self):
        """String representation of a <Booking> instance."""
        return f"Booking for {self.passenger_name} on {self.listing}"


class Review(models.Model):
    """Model representation of a <Review> instance."""
    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                 editable=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,
                                related_name='reviews')
    reviewer_name = models.CharField(max_length=128, blank=False)
    rating = models.IntegerField(validators=[MinValueValidator(1),
                                             MaxValueValidator(5)])
    comment = models.TextField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of a <Review> instance."""
        return f"Review by {self.reviewer_name} for {self.listing}"


class Payment(models.Model):
    """
    Model representation of a <Payment> instance.
    Tracks Chapa payment transactions for bookings.
    """

    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    )

    payment_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    tx_ref = models.CharField(max_length=255, unique=True)
    chapa_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """String representation of a <Payment> instance."""
        return f"Payment for {self.tx_ref} - {self.status}"

