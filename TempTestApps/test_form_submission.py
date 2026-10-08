import os
import django
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

from apps.leads.models import ContactEnquiry
from apps.leads.services import send_customer_confirmation

# Get the most recent enquiry
latest = ContactEnquiry.objects.latest('created_at')

print("=" * 60)
print(f"Testing customer confirmation for enquiry #{latest.id}")
print("=" * 60)
print(f"Name: {latest.name}")
print(f"Email: {latest.email}")
print(f"Phone: {latest.phone}")
print()

# Test sending customer confirmation
template = "leads/email/contact_confirmation.txt"
print(f"Attempting to send customer confirmation email...")
print(f"Template: {template}")
print()

result = send_customer_confirmation(latest, template)
print(f"\nResult: {result}")

if result:
    print("✓ Customer confirmation email sent successfully!")
else:
    print("✗ Customer confirmation email failed to send")
