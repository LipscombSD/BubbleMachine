from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

payment_router = DefaultRouter()
payment_router.register(r'', PaymentViewSet, basename='payments')

urlpatterns = [
    path('', include(payment_router.urls)),
]