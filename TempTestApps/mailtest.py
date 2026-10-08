import os
import sys
import django
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.conf import settings
from django.core.mail import EmailMessage
from email.utils import parseaddr

print("=" * 60)
print("EMAIL CONFIGURATION TEST")
print("=" * 60)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

# Test email extraction
def extract_email(email_string: str) -> str:
    _, addr = parseaddr(email_string)
    return addr or email_string

extracted = extract_email(settings.DEFAULT_FROM_EMAIL)
print(f"Extracted email from DEFAULT_FROM_EMAIL: {extracted}")
print()

# Test sending
print("Attempting to send test email...")
try:
    message = EmailMessage(
        subject="Test Email from Django",
        body="This is a test email from the Django mail system.",
        from_email=extracted,
        to=["engitrefinery@gmail.com"],
    )
    result = message.send(fail_silently=False)
    print(f"✓ Email sent successfully! Result: {result}")
except Exception as e:
    print(f"✗ Email failed with error:")
    print(f"  {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
