import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from apps.leads.models import ContactEnquiry

recent = ContactEnquiry.objects.all().order_by('-created_at')[:10]
print(f"Total contact enquiries: {ContactEnquiry.objects.count()}")
print("\nLast 10 submissions:")
for enquiry in recent:
    print(f"  - {enquiry.created_at}: {enquiry.display_name} ({enquiry.email})")
    print(f"    Status: {enquiry.get_status_display()}, Notified: {enquiry.notified_at}")
