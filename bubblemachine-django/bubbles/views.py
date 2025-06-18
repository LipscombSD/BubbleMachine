from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.views import subscription_or_trial_permission
from .models import BubbleSection
from .serializers import BubbleSectionSerializer

class BubbleSectionViewSet(viewsets.ModelViewSet):
    queryset = BubbleSection.objects.all()
    serializer_class = BubbleSectionSerializer
    permission_classes = [IsAuthenticated, subscription_or_trial_permission(require_subscription=True)]

    def get_queryset(self):
        return BubbleSection.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)