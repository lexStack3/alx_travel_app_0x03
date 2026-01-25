from django.urls import path, include
from rest_framework import routers, permissions
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    ListingViewSet,
    BookingViewSet,
    ReviewViewSet,
    initiate_payment,
    verify_payment
)


router = routers.DefaultRouter()
router.register('listing', ListingViewSet)
router.register('booking', BookingViewSet)
router.register('review', ReviewViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Traveling App",
        default_version="v1",
        description="API documentation for Traveling App",
        terms_of_service="http://localhost.com/terms/",
        contact=openapi.Contact(email="alexanderedimn80@gmail.com"),
        license=openapi.License(name="MIT License")
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)

urlpatterns = [
    path('', include(router.urls)),

    # Payment endpoints
    path('payments/initiate/<uuid:booking_id>/',
         initiate_payment,
         name='payment-initiate'
    ),
    path('payments/verify/',
         verify_payment,
         name='payment-verify'
    ),

    # Documentation
    path('schema.json/', schema_view.without_ui(cache_timeout=0),
         name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc')
]
