import os
import sys
import traceback

import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()
from django.test import Client
from django.test.utils import setup_test_environment

setup_test_environment()
from apps.locations.models import ServiceArea
from apps.pages.models import Page
from apps.projects.models import CaseStudy, Sector
from apps.services.models import Service, ServiceCategory

c = Client(HTTP_HOST="localhost")
urls = [
    "/",
    "/services/",
    "/contact/",
    "/emergency-callout/",
    "/sectors/",
    "/case-studies/",
    "/areas/",
    "/styleguide/",
    "/robots.txt",
    "/sitemap.xml",
    "/contact-card.vcf",
    "/contact-card-qr.svg",
    "/quote/",
    "/does-not-exist/",
    "/case-studies/?sector=restaurants",
]
urls += [c_.get_absolute_url() for c_ in ServiceCategory.objects.all()]
urls += [s.get_absolute_url() for s in Service.objects.select_related("category")]
urls += [s.get_absolute_url() for s in Sector.objects.all()]
urls += [s.get_absolute_url() for s in CaseStudy.objects.all()]
urls += [s.get_absolute_url() for s in ServiceArea.objects.all()]
urls += [
    p.get_absolute_url()
    for p in Page.objects.exclude(
        slug__in=["services", "sectors", "case-studies", "areas", "contact", "emergency-callout"]
    )
]
bad = 0
for u in urls:
    try:
        r = c.get(u)
        status = r.status_code
    except Exception as e:
        status = "EXC " + repr(e)[:200]
        traceback.print_exc()
    flag = (
        ""
        if status in (200, 302) or (u == "/does-not-exist/" and status == 404)
        else "  <-- PROBLEM"
    )
    if flag:
        bad += 1
    print(status, u, flag)
# POST tests
r = c.post(
    "/emergency-callout/", {"phone": "07778889080", "website_url": ""}, HTTP_HX_REQUEST="true"
)
print("HX emergency POST", r.status_code, r.get("HX-Trigger"), b"calling" in r.content)
r = c.post("/emergency-callout/", {"phone": "123", "website_url": ""})
print("bad emergency POST", r.status_code, b"full phone number" in r.content)
r = c.post(
    "/contact/",
    {
        "name": "A",
        "phone": "02071234567",
        "email": "a@b.com",
        "message": "hi",
        "consent": "on",
        "website_url": "",
    },
)
print("contact POST", r.status_code, r.get("Location"))
print("PROBLEMS:", bad)
