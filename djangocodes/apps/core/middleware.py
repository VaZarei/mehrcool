"""Response-header middleware: Permissions-Policy."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse

PERMISSIONS_POLICY = (
    "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), "
    "microphone=(), payment=(), usb=(), interest-cohort=()"
)


class PermissionsPolicyMiddleware:
    """Disable powerful browser features the site never uses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response.headers.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
        if request.path.startswith("/admin/"):
            response.headers.setdefault("X-Robots-Tag", "noindex, nofollow")
        return response
