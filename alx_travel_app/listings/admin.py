from django.contrib import admin
from .models import (
    User,
    Listing,
    Booking,
    Review,
    Payment
)

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Payment)
