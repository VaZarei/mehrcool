"""Deployment checks, run with ``manage.py check --deploy``."""

from __future__ import annotations

from django.conf import settings
from django.core import checks
from django.db import connections


@checks.register(checks.Tags.caches, deploy=True)
def database_cache_table_exists(app_configs, **kwargs):
    """Error if a DatabaseCache is configured but ``createcachetable``  has not been run."""
    errors = []
    for alias, conf in settings.CACHES.items():
        if not conf["BACKEND"].endswith("DatabaseCache"):
            continue
        table = conf["LOCATION"]
        with connections["default"].cursor() as cursor:
            existing = connections["default"].introspection.table_names(cursor)
        if table not in existing:
            errors.append(
                checks.Error(
                    f"Cache table '{table}' does not exist.",
                    hint="Run: python manage.py createcachetable",
                    id="core.E001",
                )
            )
    return errors
