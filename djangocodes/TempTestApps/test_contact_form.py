import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.leads.forms import ContactEnquiryForm
from apps.leads.services import send_customer_confirmation
from django.test import RequestFactory

print("=" * 60)
print("TESTING CONTACT FORM SUBMISSION")
print("=" * 60)
print()

# Create a test request
factory = RequestFactory()
request = factory.post('/contact/')

# Simulate form data
form_data = {
    'name': 'Test User',
    'company': 'Test Company',
    'phone': '07777888899',
    'email': 'engitrefinery@gmail.com',
    'enquiry_type': '',
    'equipment_type': '',
    'message': 'This is a test message from the contact form.',
    'consent': True,
    'website_url': '',  # honeypot
}

print("Form data:")
for key, value in form_data.items():
    if key != 'website_url':
        print(f"  {key}: {value}")
print()

# Create and validate form
form = ContactEnquiryForm(data=form_data)

if form.is_valid():
    print("✓ Form is valid")
    print()

    # Save the lead
    lead = form.save(commit=False)
    lead.source_url = request.build_absolute_uri()[:300]
    lead.referrer = request.headers.get("Referer", "")[:300]
    lead.user_agent = request.headers.get("User-Agent", "")[:300]
    lead.save()

    print(f"Lead saved:")
    print(f"  ID: {lead.id}")
    print(f"  Name: {lead.name}")
    print(f"  Email: {lead.email}")
    print(f"  Phone: {lead.phone}")
    print()

    # Now test sending customer confirmation
    print("Testing send_customer_confirmation...")
    template = "leads/email/contact_confirmation.txt"
    result = send_customer_confirmation(lead, template)
    print(f"Result: {result}")

    if result:
        print("✓ Customer confirmation email sent successfully!")
    else:
        print("✗ Customer confirmation email failed!")

else:
    print("✗ Form is invalid")
    print()
    print("Errors:")
    for field, errors in form.errors.items():
        print(f"  {field}: {errors}")
