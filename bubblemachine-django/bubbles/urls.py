from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BubbleSectionViewSet

router = DefaultRouter()
router.register(r'', BubbleSectionViewSet, basename='bubble-section')

urlpatterns = [
    path('', include(router.urls)),
]