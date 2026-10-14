import os
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.conf import settings

print("=" * 60)
print("EMAIL CONFIGURATION DETAILS")
print("=" * 60)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"SERVER_EMAIL: {settings.SERVER_EMAIL}")
print()

# Check if we can access email config vars
import environ
env = environ.Env()
env.read_env(Path(__file__).parent / ".env")

email_url = env("EMAIL_URL", default="")
print(f"EMAIL_URL from .env: {email_url[:20]}***")
print()

# Print email backend configuration
if hasattr(settings, 'EMAIL_HOST'):
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
if hasattr(settings, 'EMAIL_PORT'):
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
if hasattr(settings, 'EMAIL_USE_TLS'):
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
if hasattr(settings, 'EMAIL_USE_SSL'):
    print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
if hasattr(settings, 'EMAIL_HOST_USER'):
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print()

# Test sending again
from django.core.mail import EmailMessage
print("Attempting to send a test email to verify configuration...")
try:
    message = EmailMessage(
        subject="Configuration Test",
        body="Testing email configuration",
        from_email="vaahidzaarei@gmail.com",
        to=["engitrefinery@gmail.com"],
    )
    result = message.send(fail_silently=False)
    print(f"✓ Email sent! Result: {result}")
except Exception as e:
    print(f"✗ Failed: {e}")
