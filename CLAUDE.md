# CLAUDE.md — Emme Website Codebase Guide

This file provides context for AI assistants working on the emme-website repository.

## Overview

A Flask-based artist/musician CMS for Emme (emme-em.me). It provides public-facing portfolio pages and a single-admin CMS backed by SQLite. There is no JavaScript build system — all frontend code is vanilla JS and CSS embedded directly in Jinja2 templates.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Flask 3.1 |
| Auth | Flask-Login 0.6 + bcrypt 4 |
| Database | SQLite3 (WAL mode) |
| Image processing | Pillow 11 |
| Email | smtplib (stdlib) |
| Production server | Gunicorn 23 |
| Frontend | Vanilla JS + inline CSS in Jinja2 templates |

## Directory Structure

```
emme-website/
├── app.py              # Flask app factory, security middleware, blueprint registration
├── config.py           # Config class — env vars for DB, uploads, SMTP, admin credentials
├── models.py           # SQLite schema, CRUD helpers, rate-limit utilities
├── seed_data.py        # One-time DB seed script
├── requirements.txt    # Python dependencies
├── routes/
│   ├── public.py       # 11 public page routes
│   ├── admin.py        # Admin CMS routes (login, dashboard, content editors, drive)
│   └── api.py          # 40+ REST API endpoints (JSON in/out)
├── utils/
│   ├── auth.py         # Flask-Login setup, AdminUser class, create_admin()
│   ├── email.py        # SMTP contact-form email sender
│   └── uploads.py      # File upload handling, filename sanitization, thumbnail generation
├── templates/
│   ├── base.html       # Base template (extends all public pages)
│   ├── *.html          # Public page templates (about, contact, gallery, live, music, …)
│   └── admin/          # Admin-only templates (login, dashboard, content editors, drive)
├── images/             # Static images (albums/, gallery/, lighting/, soundcloud/)
├── videos/             # Static video files
└── *.html              # Pre-generated static HTML pages (mirror of templates)
```

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Create a .env file (see Environment Variables section below)
cp .env.example .env  # or create manually

# Start the dev server
python app.py  # runs on http://localhost:5001 with debug=True
```

## Environment Variables

All secrets are loaded from `.env` via python-dotenv. The `.env` file is gitignored.

| Variable | Default | Purpose |
|---|---|---|
| `FLASK_SECRET_KEY` | random hex | Session signing key |
| `ADMIN_USERNAME` | `emme` | Admin login username |
| `ADMIN_PASSWORD` | *(required to create admin)* | Admin login password — triggers admin account creation on startup |
| `SMTP_HOST` | | Outgoing mail server |
| `SMTP_PORT` | | SMTP port |
| `SMTP_USER` | | SMTP auth username |
| `SMTP_PASS` | | SMTP auth password |
| `SMTP_FROM` | | From address for contact emails |
| `CONTACT_EMAIL` | `booking@emme-em.me` | Recipient for contact form submissions |
| `DRIVE_FOLDER` | | Root path for the admin file manager |

## Database

SQLite file at `emme.db` (gitignored). Tables:

| Table | Purpose |
|---|---|
| `admin_user` | Single admin account |
| `page_content` | Key-value JSON content per page/section |
| `gallery_images` | Gallery images with alt text and sort order |
| `live_videos` | Embedded performance videos |
| `shows` | Concert/show listings |
| `releases` | Music releases/albums |
| `soundcloud_tracks` | SoundCloud track links |
| `archive_articles` | Archived articles (Nest HQ etc.) |
| `lighting_shows` | Lighting design credits with JSON links |
| `lighting_photos` | Lighting portfolio photos |
| `contact_messages` | Contact form submissions |
| `login_attempts` | Rate-limiting data |

**Conventions:**
- `sort_order INTEGER DEFAULT 0` for ordered lists
- Booleans stored as `INTEGER` (0/1)
- Flexible content stored as JSON strings in `content_json` or `links_json` columns
- Timestamps use `CURRENT_TIMESTAMP`
- WAL mode and foreign keys are enabled at connection time in `models.py`

## Route Map

### Public (`routes/public.py`)
- `GET /` — Homepage
- `GET /about` — About page
- `GET /contact` — Contact form
- `GET /gallery` — Photo gallery
- `GET /live` — Live shows + videos
- `GET /music` — Releases + tracks
- `GET /shop` — Redirect to external shop
- `GET /blog` — Blog posts
- `GET /lighting` — Lighting design portfolio
- `GET /archive` — Article archive

### Admin (`routes/admin.py`) — requires login
- `GET|POST /admin/login` — Login (rate-limited: 5 attempts / 5 min per IP)
- `GET /admin/logout`
- `GET /admin/` — Dashboard
- `GET /admin/edit/<page>` — Rich content editor for a page (about, index, shop, contact, blog)
- `GET /admin/gallery|live|music|lighting|archive` — Section-specific CRUD editors
- `GET|POST /admin/messages` — View/mark-read contact messages
- `GET /admin/drive[/<path>]` — File manager
- `POST /admin/drive-upload|drive-download|drive-mkdir|drive-delete`

### API (`routes/api.py`) — JSON, admin auth required except contact
- `POST /api/contact` — Contact form (rate-limited: 10 / 10 min per IP)
- `POST /api/save-content` — Persist page content JSON
- `POST /api/upload` — File upload
- CRUD routes for: `gallery`, `shows`, `videos`, `releases`, `tracks`, `lighting-shows`, `lighting-photos`, `archive`, `blog-posts`, `messages`

## Security Patterns

Do not remove or weaken these — they are load-bearing:

- **CSRF:** Token generated per request, stored in a cookie (not HttpOnly) and verified against the `X-CSRF-Token` header on state-changing requests.
- **Rate limiting:** IP-based using `login_attempts` table. Login: 5/5 min. Contact form: 10/10 min.
- **SQL injection:** `models.py` uses whitelists (`VALID_TABLES`, `VALID_ORDER_COLUMNS`) for any dynamic table/column names; all values use parameterized queries.
- **Path traversal:** `_safe_drive_path()` in `admin.py` enforces that all drive operations stay within `DRIVE_FOLDER`.
- **File uploads:** Filenames sanitized to alphanumeric + `._- `. Files renamed to UUIDs. Extensions checked against allowlists.
- **Session cookies:** `HttpOnly=True`, `SameSite=Lax`, 1-hour lifetime.
- **Security headers:** Set on every response — `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`.
- **Passwords:** bcrypt with 4 rounds.

## Frontend Conventions

- **No build step.** CSS and JS live inline inside `<style>` and `<script>` tags inside `.html` templates.
- **Template inheritance:** All public pages extend `templates/base.html` via `{% extends 'base.html' %}` and fill `{% block title %}`, `{% block head %}`, and `{% block body %}`.
- **Custom filter:** `|timestamp` converts Unix timestamps to human-readable dates.
- **Admin UI:** Dark theme (`#111` background, Calibri font), minimal functional design.
- **Public UI:** Modern design with Inter font, glitch animations; CSS variables define color palette.
- **Reorder pattern:** Drag-to-reorder with a `sort_order` field; reorder API endpoints accept an ordered array of IDs.

## API Response Format

All API endpoints return JSON:

```json
{ "status": "ok" }
{ "status": "error", "message": "Human-readable error" }
```

Input length limits are enforced by constants at the top of `api.py` (e.g., `_MAX_NAME`, `_MAX_EMAIL`).

## Making Changes

### Adding a new public page
1. Add a route in `routes/public.py`
2. Create `templates/<page>.html` extending `base.html`
3. If the page has editable content, add a row to `page_content` in `seed_data.py` and a case in `/api/save-content`

### Adding a new content type
1. Define the table in `models.py` `SCHEMA` string and add helper functions
2. Add CRUD endpoints in `routes/api.py`
3. Add an admin editor template in `templates/admin/`
4. Add the admin route in `routes/admin.py`

### Adding a new API endpoint
- Follow the pattern in `routes/api.py`: parse JSON body, validate inputs, call model helper, return `{status: 'ok'}` or `{status: 'error', message: '...'}`
- Add CSRF verification (`request.headers.get('X-CSRF-Token')`) for all state-changing endpoints

## Testing

There is no test suite. Manual testing via the browser and `curl` is the current approach. When adding a test framework, `pytest` is the natural choice given the Flask codebase.

## Deployment

Production is served by Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

No CI/CD pipeline is configured. No Dockerfile exists. The `emme.db` and `static/uploads/` are gitignored and must exist on the production server.
