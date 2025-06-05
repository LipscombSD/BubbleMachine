import logging
import stripe
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import permissions

from app import settings
from .models import User
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, CustomTokenRefreshSerializer
)

stripe.api_key = settings.STRIPE_API_KEY

logger = logging.getLogger(__name__)

class CustomTokenRefreshView(TokenRefreshView):
    """Used to convert refresh/access to refresh_token/access_token"""
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the original refresh token from request
        refresh_token = request.data.get('refresh_token')

        # Get the new access token from serializer
        access_token = serializer.validated_data.get('access')

        # Return custom response
        return Response({
            'access_token': str(access_token),
            'refresh_token': refresh_token
        }, status=status.HTTP_200_OK)

def subscription_or_trial_permission(require_subscription=False, require_trial=False):
    """Factory function to create a SubscriptionOrTrialPermission class"""
    class SubscriptionOrTrialPermission(permissions.BasePermission):
        message = (
            "You must be subscribed and have an active trial to access this endpoint."
            if require_subscription and require_trial
            else "You must be subscribed to access this endpoint."
            if require_subscription
            else "Your trial has ended. Please subscribe to continue."
            if require_trial
            else "Access denied."
        )

        def has_permission(self, request, view):
            user = request.user
            if not user or not user.is_authenticated:
                return False

            # Superusers bypass all checks
            if user.is_superuser:
                return True

            # Check subscription status if required
            subscription_ok = not require_subscription or user.is_subscribed

            # Check trial status if required
            trial_ok = not require_trial or user.is_trial_active

            return subscription_ok and trial_ok

    return SubscriptionOrTrialPermission

class UserViewSet(GenericViewSet):
    """User endpoints"""
    queryset = User.objects.all()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """User registration endpoint"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """User login endpoint"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            logger.info(f"User logged in: {user.email}")
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, subscription_or_trial_permission(require_trial=True)]
    )
    def profile(self, request):
        """Get user profile endpoint (requires active trial or subscription)"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'patch'],
        permission_classes=[IsAuthenticated, subscription_or_trial_permission(require_subscription=True)]
    )
    def update_profile(self, request):
        """Update user profile endpoint (requires subscription)"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Profile updated for user: {request.user.email}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def create_checkout_session(self, request):
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, price_1234) of the product you want to sell
                        'price': 'price_1RWkiDCIYopQMgnow3bE86e1',
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=settings.WEBSITE_DOMAIN + '?success=true',
                cancel_url=settings.WEBSITE_DOMAIN + '?canceled=true',
            )
            return HttpResponseRedirect(checkout_session.url)
        except Exception as e:
            return Response({'error': str(e)}, status=500)