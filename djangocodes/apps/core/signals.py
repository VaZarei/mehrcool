"""Cache invalidation when trust content changes."""

from __future__ import annotations

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .constants import NAVIGATION_CACHE_KEY, SITE_SETTINGS_CACHE_KEY
from .models import BrandServiced, ClientLogo, IntentCard, TrustBadge


@receiver([post_save, post_delete], sender=TrustBadge)
@receiver([post_save, post_delete], sender=BrandServiced)
@receiver([post_save, post_delete], sender=ClientLogo)
@receiver([post_save, post_delete], sender=IntentCard)
def clear_site_caches(**kwargs: object) -> None:
    """Drop cached settings/navigation so header and footer fragments refresh.

    Args:
        **kwargs: Signal arguments (unused).
    """
    cache.delete_many([SITE_SETTINGS_CACHE_KEY, NAVIGATION_CACHE_KEY])
