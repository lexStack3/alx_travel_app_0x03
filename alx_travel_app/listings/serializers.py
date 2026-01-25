from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Listing, Booking, Review


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """."""
    class Meta:
        model = User
        fields = [
            'user_id', 'first_name',
            'last_name', 'email',
            'username'
        ]


class ListingSerializer(serializers.ModelSerializer):
    """."""
    operator = UserSerializer(read_only=True)
    class Meta:
        model = Listing
        fields = [
            'listing_id', 'operator',
            'transport_type', 'name',
            'description', 'departure_time',
            'price', 'available_seats',
            'total_seats', 'status'
        ]
        read_only_fields = ['operator']


class BookingSerializer(serializers.ModelSerializer):
    """."""
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing_id',
            'passenger_name', 'passenger_email',
            'num_seats', 'booking_date',
            'amount_paid', 'status'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    """."""
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
    )
    listing_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'review_id', 'listing_id',
            'listing_name', 'reviewer_name',
            'rating', 'comment'
        ]
        read_only_fields = ['listing']

    def get_listing_name(self, obj):
        """
        Returns name of the <Listing> instance.
        """
        return obj.listing.name
