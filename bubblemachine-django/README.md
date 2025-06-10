
# BubbleMachine Django Backend

A Django-based REST API for user management.

## Setup and Running
1. Install Docker: Follow instructions at [docker.com](https://www.docker.com/get-started).
2. Clone this repository:
   ```bash
   git clone <repository-url>
   cd bubblemachine-django
   ```
3. Build the Docker images:
   ```bash
   docker compose build
   ```
4. Run the application:
   ```bash
   docker compose up
   ```
   The API will be available at `http://localhost:8000`.

## Running Tests
To run tests on the users app:
```bash
docker compose run --rm app sh -c "python3 manage.py test users.tests"
```

## Testing Stripe
1. Install the Stripe CLI:
   ```bash
   brew install stripe/stripe-cli/stripe
   ```
2. Login to Stripe:
   ```bash
   stripe login
   ```
3. Forward webhook to internet:
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/payments/stripe_payment_webhook/
   # Dont forget to set STRIPE_WEBHOOK_SECRET to the provided value for testing
   ```
4. Mock stripe events:
- `stripe trigger customer.subscription.created`
- `stripe trigger customer.subscription.updated`
- `stripe trigger customer.subscription.deleted`

## API Endpoints
- **POST /users/register/**: Register a new user
- **POST /users/login/**: Login and obtain JWT tokens
- **POST /users/login/refresh/**: Refresh JWT access token
- **POST /users/logout/**: Logout and blacklist refresh token
- **GET /users/profile/**: Get user profile
- **PUT/PATCH /users/update_profile/**: Update user profile
- **POST /users/process_payment/**: Simulate payment to upgrade to permanent account
