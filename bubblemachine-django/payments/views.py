import json
import logging
import stripe
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated

from app import settings
from users.models import User
from .models import Subscription

stripe.api_key = settings.STRIPE_API_KEY
logger = logging.getLogger(__name__)


class PaymentViewSet(GenericViewSet):
    """Payment endpoints"""

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def create_checkout_session(self, request):
        """Create a user checkout session"""
        user = request.user
        # Create a Stripe customer if not already exists
        if not user.stripe_customer_id:
            try:
                customer = stripe.Customer.create(email=user.email)
                user.stripe_customer_id = customer.id
                user.save()
            except stripe.error.StripeError as e:
                return Response({'message': str(e)}, status=500)
        try:
            checkout_session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,  # Use existing customer
                line_items=[
                    {
                        'price': 'price_1RWkiDCIYopQMgnow3bE86e1',  # Replace with your Price ID
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=settings.WEBSITE_DOMAIN + 'app/?success=true',
                cancel_url=settings.WEBSITE_DOMAIN + 'app/?success=false',
            )
            return Response({'checkout_session_url': checkout_session.url}, status=200)

        except stripe.error.StripeError as e:
            return Response({'message': str(e)}, status=500)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    @csrf_exempt
    def stripe_payment_webhook(self, request):
        """Webhook to retrieve an event from stripe"""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return Response({'message': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return Response({'message': 'Invalid signature'}, status=400)

        logger.info(f"Webhook '{event.type}' for event: {event.id}")

        # Handle subscription events
        if event.type in ['customer.subscription.created', 'customer.subscription.updated',
                          'customer.subscription.deleted']:
            subscription = event.data.object
            customer_id = subscription.customer
            try:
                user = User.objects.get(stripe_customer_id=customer_id)
                # Update or create subscription record
                sub, created = Subscription.objects.update_or_create(
                    user=user,
                    stripe_subscription_id=subscription.id,
                    defaults={'status': subscription.status}
                )
                # Set is_subscribed based on active subscriptions
                has_active_sub = user.subscriptions.filter(
                    status__in=['active', 'trialing', 'past_due']
                ).exists()
                user.is_subscribed = has_active_sub
                user.save()
            except User.DoesNotExist:
                logger.warning(f"No user found for customer {customer_id}")

        return Response(status=200)
