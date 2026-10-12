# Mehr Cool Refrigeration & Air Conditioning — website

Production-grade Django site for MEHR COOL REFRIGERATION & AIR CONDITIONING LTD (Canary Wharf,
London). Server-rendered HTML, HTMX for interactivity, hand-written CSS in explicit literal
values, and an admin panel in which every word, image, number and link on the public site is
editable.

## Stack

| Layer | Choice | Why |
| --- | --- | --- |
| Framework | Django 6.1, Python 3.12+ | Latest stable; batteries included (admin, sitemaps, redirects) |
| Interactivity | HTMX 2 (vendored) + small ES modules | No SPA; every page works with JavaScript disabled |
| CSS | Hand-written, ITCSS layers, literal values only | No framework, and no custom properties: a selector states the colour or size it paints |
| Database | SQLite (local and production) | Single file, `djangocodes/db.sqlite3`; path overridable via `DATABASE_URL` |
| Static files | WhiteNoise + `CompressedManifestStaticFilesStorage` | Hashed filenames, one-year cache, Cloudflare-ready |
| Images | Pillow renditions (AVIF/WebP/JPEG, `srcset`) | In-house `djangocodes/apps/core/images.py`; no extra dependency |

Third-party packages and the one-line reason for each are in `requirements/base.txt`,
`requirements/local.txt` and `requirements/production.txt`.

## Project layout

```
djangocodes/config/            settings (base / local / production), urls, wsgi, asgi
djangocodes/apps/
  core/            SiteSettings singleton, navigation, trust badges, homepage, template tags,
                   image renditions, placeholders, seed data, management commands
  seo/             SEOFieldsModel, schema.org builders, sitemaps, robots.txt, redirects admin
  pages/           Page + block system (ContentBlockBase → PageBlock, ServiceBlock)
  services/        ServiceCategory, Service, specs, FAQs
  projects/        Sector, CaseStudy
  locations/       ServiceArea (borough landing pages)
  testimonials/    Testimonial
  leads/           ContactEnquiry, RepairRequest, FormFieldChoice, LeadNote
djangocodes/templates/         base.html, partials/, one folder per app
djangocodes/static/css/        style.css (single stylesheet)
djangocodes/static/js/         main.js entry + one module per behaviour, vendor/htmx.min.js
djangocodes/media/placeholders demo media shipped with the repo (see ASSETS_NEEDED.md)
djangocodes/fixtures/demo.json full demo dataset (python manage.py loaddata djangocodes/fixtures/demo.json)
```

## Local setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements/local.txt
copy .env.production.example .env    # cp on macOS/Linux; then set local values (see Environment variables)
python manage.py migrate
python manage.py seed_demo           # populates everything + generates placeholder media
python manage.py createsuperuser
python manage.py runserver
```

Then open <http://127.0.0.1:8000/> and <http://127.0.0.1:8000/admin/>.
The design system is at <http://127.0.0.1:8000/styleguide/> (local only).

`seed_demo` is idempotent: re-running it updates seeded rows by slug and leaves anything you
added alone. Alternatively load the fixture snapshot:

```bash
python manage.py loaddata djangocodes/fixtures/demo.json
```

The fixture references media under `djangocodes/media/placeholders/`, which is committed, so the site is
fully populated from a clean checkout.

## Everyday commands

| Task | Command |
| --- | --- |
| Run tests | `python manage.py test djangocodes/apps` |
| Format | `black .` (config in `pyproject.toml`) |
| Lint | `ruff check .` |
| Regenerate placeholder media | `python manage.py make_placeholders` |
| Create admin groups (Content Editor / Sales) | `python manage.py setup_groups` |
| Docker (production) | `docker compose up -d --build` |
| URL smoke test against the local DB | `python djangocodes/scripts/smoke_urls.py` |
| Deployment checklist | `python manage.py check --deploy` (with production env) |

### CSS workflow

Edit `djangocodes/static/css/style.css` directly; it is served as-is in both DEBUG and production, no
build step or `collectstatic` transform required beyond the normal static file hashing.

One rule the stylesheet relies on:

- **No CSS custom properties.** Every declaration carries its literal value, so a selector can
  be read on its own. The palette and the type/spacing ladders are listed on `/styleguide/`
  (dev only) and in `djangocodes/apps/core/views.py`.

## Environment variables

Template: `.env.production.example`. Summary:

| Variable | Purpose |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.local` or `config.settings.production` |
| `SECRET_KEY` | Long random string; required in production |
| `DEBUG` | `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated `https://` origins |
| `DATABASE_URL` | `sqlite:////app/djangocodes/db.sqlite3` in production; defaults to `djangocodes/db.sqlite3` locally |
| `CONN_MAX_AGE` | Persistent DB connection lifetime in seconds (default 60) |
| `EMAIL_URL` | e.g. `smtp+tls://user:pass@smtp.example.com:587`; `consolemail://` locally |
| `DEFAULT_FROM_EMAIL` | Sender for lead notifications |
| `LEAD_NOTIFICATION_EMAIL` | Fallback recipient if Site settings leaves it blank |
| `SITE_URL` | Canonical origin, used in sitemaps, canonical tags and JSON-LD |
| `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT` | Security headers (production) |
| `EMERGENCY_PHONE_FALLBACK`, `TRADING_NAME_FALLBACK` | Used only by the 500 page if the DB is down |
| `LOG_FILE` | Optional path for a size-rotated log file (production) |
| `STYLEGUIDE_ENABLED` | Expose `/styleguide/` (default off) |

## Deploying

1. Set the variables above (`DJANGO_SETTINGS_MODULE=config.settings.production`). Production uses SQLite:
   the database file must sit on persistent storage (a mounted volume) and be included in backups.
2. `pip install -r requirements/production.txt`
3. `python manage.py collectstatic --noinput`
4. `python manage.py migrate && python manage.py createcachetable`
5. Either `python manage.py loaddata djangocodes/fixtures/demo.json` for a demo, or `seed_demo`, or start empty and
   fill Site settings in the admin (the singleton is created on first request with sensible defaults).
6. `python manage.py setup_groups`
7. Run `gunicorn config.wsgi --bind 0.0.0.0:8000 --workers 3` behind Cloudflare / nginx. WhiteNoise serves
   `/static/` with immutable cache headers; serve `/media/` from nginx or object storage.
8. `python manage.py check --deploy` should report no issues.

Production database: SQLite (`djangocodes/db.sqlite3`). Back it up while the site is running with
`sqlite3 db.sqlite3 ".backup backup.sqlite3"` (copying the raw file during writes can corrupt it).
SQLite allows one writer at a time, which is fine for a brochure site with lead forms; keep
workers modest and avoid long write transactions.

Media uploads live in `MEDIA_ROOT` (`djangocodes/media/`). Renditions are generated lazily into
`djangocodes/media/renditions/` and can be deleted at any time.

## Architecture notes

- **Everything is admin-editable.** `SiteSettings` (pk=1) holds identity, contact details, hero
  content, CTA copy, analytics IDs and SEO defaults. Index pages (`/services/`, `/sectors/`,
  `/case-studies/`, `/areas/`, `/contact/`, `/emergency-callout/`) read their heading and intro from
  `Page` rows with those reserved slugs. A test asserts no template contains contact details.
- **URL dispatch.** `/<slug>/` is shared by category hubs and pages via
  `djangocodes.apps.core.views.slug_dispatch` (category first, then page). Everything else has an explicit route
  registered before it.
- **Blocks.** `ContentBlockBase` is abstract; `PageBlock` and `ServiceBlock` are concrete. Each block
  type renders from `djangocodes/templates/pages/blocks/<type>.html`, so a new block type is a choice + a partial.
- **Schema.org** is built in `djangocodes/apps/seo/schema.py` from the database and emitted via `{% json_ld %}`.
- **Performance.** Header/footer/nav fragments are cached; context processors cache settings,
  navigation and badges; every listing uses `select_related`/`prefetch_related` and query budgets are
  asserted in `djangocodes/apps/core/tests/test_queries.py`. The hero video is never downloaded on phones, on
  reduced-motion, on Save-Data, or on 2G.
- **Extending.** Add a new app under `djangocodes/apps/`, inherit `TimeStampedModel` / `PublishableModel` /
  `SEOFieldsModel`, register a sitemap in `djangocodes/apps/seo/sitemaps.py` and a URL include in `djangocodes/config/urls.py`.
  Nothing existing needs to change.

## Also read

- `ADMIN_GUIDE.md` — plain-English guide for the client.
- `ASSETS_NEEDED.md` — every placeholder to replace, with dimensions and budgets.
- `COPY_TO_VERIFY.md` — every factual claim in the seeded copy that needs confirming.
