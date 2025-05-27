FROM python:3.11-slim

LABEL maintainer="rvsteele@sdsu.edu"

WORKDIR /app

# Install system packages
RUN apt-get update
RUN apt-get install -y postgresql-client

# Copy and install pip packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files into workdir
COPY . .

# Create dir for logs
RUN mkdir -p logs

# Collect static files and run migrations
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]