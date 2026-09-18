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
| Database | SQLite (local), PostgreSQL (production) | Configured via `DATABASE_URL` |
| Static files | WhiteNoise + `CompressedManifestStaticFilesStorage` | Hashed filenames, one-year cache, Cloudflare-ready |
| Images | Pillow renditions (AVIF/WebP/JPEG, `srcset`) | In-house `apps/core/images.py`; no extra dependency |

Third-party packages and the one-line reason for each are in `requirements/base.txt`,
`requirements/local.txt` and `requirements/production.txt`.

## Project layout

```
config/            settings (base / local / production), urls, wsgi, asgi
apps/
  core/            SiteSettings singleton, navigation, trust badges, homepage, template tags,
                   image renditions, placeholders, seed data, management commands
  seo/             SEOFieldsModel, schema.org builders, sitemaps, robots.txt, redirects admin
  pages/           Page + block system (ContentBlockBase → PageBlock, ServiceBlock)
  services/        ServiceCategory, Service, specs, FAQs
  projects/        Sector, CaseStudy
  locations/       ServiceArea (borough landing pages)
  testimonials/    Testimonial
  leads/           ContactEnquiry, EmergencyCallout, FormFieldChoice, LeadNote
templates/         base.html, partials/, one folder per app
static/css/        02-reset … 08-preferences, 05-components/*.css, main.css (import index)
static/js/         main.js entry + one module per behaviour, vendor/htmx.min.js
media/placeholders demo media shipped with the repo (see ASSETS_NEEDED.md)
fixtures/demo.json full demo dataset (python manage.py loaddata fixtures/demo.json)
```

## Local setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements/local.txt
copy .env.example .env               # cp on macOS/Linux; defaults are fine for local dev
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
python manage.py loaddata fixtures/demo.json
```

The fixture references media under `media/placeholders/`, which is committed, so the site is
fully populated from a clean checkout.

## Everyday commands

| Task | Command |
| --- | --- |
| Run tests | `python manage.py test apps` |
| Format | `black .` |
| Lint | `ruff check .` |
| Build CSS bundles (after editing any CSS) | `python manage.py build_css` |
| Regenerate placeholder media | `python manage.py make_placeholders` |
| Create admin groups (Content Editor / Sales) | `python manage.py setup_groups` |
| URL smoke test against the local DB | `python scripts/smoke_urls.py` |
| Deployment checklist | `python manage.py check --deploy` (with production env) |

### CSS workflow

Edit the source layers in `static/css/`. Locally `DEBUG=True` loads `main.css`, which
`@import`s every layer so changes appear immediately. Before deploying run
`python manage.py build_css`, which concatenates the layers in `main.css` order into
`main.min.css` (loaded deferred) and `critical.min.css` (inlined into `<head>`).
`collectstatic` then hashes both.

Two rules the layers rely on:

- **No CSS custom properties.** Every declaration carries its literal value, so a selector can
  be read on its own. The palette and the type/spacing ladders are listed on `/styleguide/`
  (dev only) and in `apps/core/views.py`; change a value in the layer that paints it.
- **`08-preferences.css` is the accessibility layer, and it is generated.** Because there is no
  `:root` block to re-declare, `prefers-reduced-motion`, `prefers-reduced-transparency` and
  `prefers-contrast` are honoured by per-selector overrides in that one file, loaded last so it
  wins on equal specificity. After adding a transition, a blurred surface or a hairline border,
  run `python scripts/gen_preferences.py` (then `build_css`) rather than editing it. It is not
  inlined as critical CSS; the above-the-fold motion it would suppress is handled by a small
  `prefers-reduced-motion` block at the end of `06-animations.css`.

## Environment variables

See `.env.example`. Summary:

| Variable | Purpose |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.local` or `config.settings.production` |
| `SECRET_KEY` | Long random string; required in production |
| `DEBUG` | `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated `https://` origins |
| `DATABASE_URL` | `postgres://user:pass@host:5432/db` or `sqlite:///db.sqlite3` |
| `EMAIL_URL` | e.g. `smtp+tls://user:pass@smtp.example.com:587`; `consolemail://` locally |
| `DEFAULT_FROM_EMAIL` | Sender for lead notifications |
| `LEAD_NOTIFICATION_EMAIL` | Fallback recipient if Site settings leaves it blank |
| `SITE_URL` | Canonical origin, used in sitemaps, canonical tags and JSON-LD |
| `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT` | Security headers (production) |
| `EMERGENCY_PHONE_FALLBACK`, `TRADING_NAME_FALLBACK` | Used only by the 500 page if the DB is down |
| `STYLEGUIDE_ENABLED` | Expose `/styleguide/` (default off) |

## Deploying

1. Provision PostgreSQL and set the variables above (`DJANGO_SETTINGS_MODULE=config.settings.production`).
2. `pip install -r requirements/production.txt`
3. `python manage.py build_css && python manage.py collectstatic --noinput`
4. `python manage.py migrate && python manage.py createcachetable`
5. Either `python manage.py loaddata fixtures/demo.json` for a demo, or `seed_demo`, or start empty and
   fill Site settings in the admin (the singleton is created on first request with sensible defaults).
6. `python manage.py setup_groups`
7. Run `gunicorn config.wsgi --bind 0.0.0.0:8000 --workers 3` behind Cloudflare / nginx. WhiteNoise serves
   `/static/` with immutable cache headers; serve `/media/` from nginx or object storage.
8. `python manage.py check --deploy` should report no issues.

Media uploads live in `MEDIA_ROOT` (`media/`). Renditions are generated lazily into
`media/renditions/` and can be deleted at any time.

## Architecture notes

- **Everything is admin-editable.** `SiteSettings` (pk=1) holds identity, contact details, hero
  content, CTA copy, analytics IDs and SEO defaults. Index pages (`/services/`, `/sectors/`,
  `/case-studies/`, `/areas/`, `/contact/`, `/emergency-callout/`) read their heading and intro from
  `Page` rows with those reserved slugs. A test asserts no template contains contact details.
- **URL dispatch.** `/<slug>/` is shared by category hubs and pages via
  `apps.core.views.slug_dispatch` (category first, then page). Everything else has an explicit route
  registered before it.
- **Blocks.** `ContentBlockBase` is abstract; `PageBlock` and `ServiceBlock` are concrete. Each block
  type renders from `templates/pages/blocks/<type>.html`, so a new block type is a choice + a partial.
- **Schema.org** is built in `apps/seo/schema.py` from the database and emitted via `{% json_ld %}`.
- **Performance.** Header/footer/nav fragments are cached; context processors cache settings,
  navigation and badges; every listing uses `select_related`/`prefetch_related` and query budgets are
  asserted in `apps/core/tests/test_queries.py`. The hero video is never downloaded on phones, on
  reduced-motion, on Save-Data, or on 2G.
- **Extending.** Add a new app under `apps/`, inherit `TimeStampedModel` / `PublishableModel` /
  `SEOFieldsModel`, register a sitemap in `apps/seo/sitemaps.py` and a URL include in `config/urls.py`.
  Nothing existing needs to change.

## Also read

- `ADMIN_GUIDE.md` — plain-English guide for the client.
- `ASSETS_NEEDED.md` — every placeholder to replace, with dimensions and budgets.
- `COPY_TO_VERIFY.md` — every factual claim in the seeded copy that needs confirming.
