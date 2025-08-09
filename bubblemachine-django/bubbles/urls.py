from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SongViewSet, BubbleViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'songs', SongViewSet, basename='song')
router.register(r'bubbles', BubbleViewSet, basename='bubble')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]