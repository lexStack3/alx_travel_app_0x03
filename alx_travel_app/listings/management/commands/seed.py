import random
from django_seed import Seed
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from alx_travel_app.listings.models import (
    Listing,
    Booking,
    Review
)


User = get_user_model()


def run():
    seeder = Seed.seeder()

    print("Creating 5 Users...")
    seeder.add_entity(User, 5, {
        "first_name": lambda x: seeder.faker.first_name(),
        "last_name": lambda x: seeder.faker.last_name(),
        "email": lambda x: seeder.faker.unique.email(),
        "username": lambda x: seeder.faker.unique.user_name()
    })

    print("Creating 10 Listing instances...")
    seeder.add_entity(Listing, 10, {
        "operator": lambda x: User.objects.order_by("?").first(),
        "transport_type": lambda x: random.choice(['bus', 'train', 'flight', 'boat']),
        "name": lambda x: seeder.faker.city(),
        "description": lambda x: seeder.faker.text(max_nb_char=200),
        "origin": lambda x: "NG-LA",
        "destination": lambda x: "NG-CR",
        "departure_time": lambda x: timezone.now(),
        "price": lambda x: round(random.uniform(5000, 30000), 2),
        "total_seats": lambda x: random.randint(20, 60),
        "available_seats": lambda x: random.randint(5, 30),
        "status": lambda x: random.choice(["active", "confirmed", "cancelled"]),
    })

    print("Creating 20 Booking instances...")
    seeder.add_entity(Booking, 20, {
        "listing": lambda x: Listing.objects.order_by("?").first(),
        "passenger_name": lambda x: seeder.faker.name(),
        "passenger_email": lambda x: seeder.faker.email(),
        "num_seats": lambda x: random.randint(1, 4),
        "booking_date": lambda x: timezone.now(),
        "amount_paid": lambda x: round(random.uniform(3000, 20000), 2),
        "status": lambda x: random.choice(["pending", "confirmed", "cancelled"]),
    })

    print("Creating 30 Review instances...")
    seeder.add_entity(Review, 30, {
        "listing": lambda x: Listing.objects.order_by("?").first(),
        "reviewer_name": lambda x: seeder.faker.name(),
        "rating": lambda x: random.randint(1, 5),
        "comment": lambda x: seeder.faker.sentence(),
    })

    seeder.execute()
    print("Database seeded successfully!")


class Command(BaseCommand):
    help = "Seed database with initial data"

    def handle(self, *args, **kwargs):
        run()
