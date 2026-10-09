"""Cache-based rate limiting for public lead forms (no extra dependencies)."""

from __future__ import annotations

from functools import wraps
from typing import Any

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse

# (scope, max POSTs, window seconds). Per client IP.
IP_LIMIT = (5, 600)
# Per submitted email address: stops the form being used to mail third parties.
EMAIL_LIMIT = (3, 3600)
# Per form, across all clients: caps a distributed flood.
GLOBAL_LIMIT = (200, 3600)


def client_ip(request: HttpRequest) -> str:
    """Best-effort client IP (Cloudflare header first, then the socket address)."""
    return request.META.get("HTTP_CF_CONNECTING_IP") or request.META.get("REMOTE_ADDR", "unknown")


def hit(key: str, limit: int, window: int) -> bool:
    """Count one event; return True when ``key`` has exceeded ``limit`` in ``window`` seconds."""
    cache.add(key, 0, window)
    try:
        return cache.incr(key) > limit
    except ValueError:
        cache.set(key, 1, window)
        return False


def is_limited(request: HttpRequest, scope: str) -> bool:
    """Whether this POST breaches the per-IP or global limit for ``scope``."""
    return hit(f"rl:{scope}:ip:{client_ip(request)}", *IP_LIMIT) or hit(
        f"rl:{scope}:all", *GLOBAL_LIMIT
    )


def email_limited(scope: str, email: str) -> bool:
    """Whether ``email`` has already received too many messages from ``scope``."""
    email = (email or "").strip().lower()
    return bool(email) and hit(f"rl:{scope}:mail:{email}", *EMAIL_LIMIT)


def throttle_post(scope: str):
    """Decorator for function views: reject over-limit POSTs with HTTP 429."""

    def decorator(view):
        @wraps(view)
        def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
            if request.method == "POST" and is_limited(request, scope):
                return too_many(request)
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


def too_many(request: HttpRequest) -> HttpResponse:
    """429 response, JSON for the repair wizard's fetch call, plain text otherwise."""
    msg = "Too many requests. Please wait a few minutes or call us directly."
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": False, "errors": {"__all__": [msg]}}, status=429)
    return HttpResponse(msg, status=429, content_type="text/plain")
