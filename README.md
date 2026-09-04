# Zoo Quest

**Turn a day at the zoo into an adventure.**

Families scan QR markers around a zoo, discover animals, complete challenges, earn XP and unlock badges. The phone is the controller; the zoo is the game board. Long-term, a multi-tenant platform zoos manage themselves.

The full design is in [`docs/blueprint-v0.1.html`](docs/blueprint-v0.1.html) (architecture, MVP scope, user flow, schema, API, frontend, admin, roadmap). Read Section 0 first.

## Layout

```
zoo-quest/
├── apps/
│   ├── api/          Django 5 + DRF        → Railway
│   │   ├── apps/     tenants · content · play · analytics · core
│   │   ├── config/   settings/{base,local,production,test}.py, urls.py
│   │   └── fixtures/ cedar_hollow_seed.json (fictional test zoo) + generator script
│   └── web/          Next.js 16 + TypeScript + Tailwind 4 (PWA) → Vercel
├── docs/             blueprint and later design notes
├── docker-compose.yml  local Postgres only
└── Makefile          shortcuts: make db / api / web / test / lint / seed
```

## Run it locally

Prerequisites: Python 3.11+, Node 22+, Docker (for Postgres). One-time setup:

```bash
git clone <this repo> && cd zoo-quest
docker compose up -d db                                  # Postgres on :5432

# API
cd apps/api
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser                         # for /admin/
python manage.py loaddata fixtures/cedar_hollow_seed.json   # the fictional test zoo
cd ../..

# Web
cd apps/web
npm install
cp .env.example .env.local
cd ../..
```

Every day after that, in two terminals:

```bash
make api      # http://localhost:8000  → /api/v1/health/  /admin/  /api/docs/
make web      # http://localhost:3000
```

Tests and lint: `make test`, `make lint`. CI runs the same on every push.

## Deploy

| Piece | Where | How |
|---|---|---|
| API + Postgres | [Railway](https://railway.app) | New project → Deploy from GitHub → root directory `apps/api`. Add a Postgres plugin; Railway injects `DATABASE_URL`. Set `DJANGO_SETTINGS_MODULE=config.settings.production`, `SECRET_KEY` (50+ random chars), `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` (your Vercel URL), and `PLAY_BASE_URL` (the Vercel URL; printed QR codes point here). Generate a domain with target port **8080** (Railway's `$PORT`). `railway.json` handles build, migrate and health check. |
| Web | [Vercel](https://vercel.com) | Import the repo → root directory `apps/web`. Set `NEXT_PUBLIC_API_URL=https://<railway-domain>/api/v1`. |

## Milestones

- [x] **M0 Foundation** — this. Repo, settings split, four apps, health endpoint, route skeleton, CI, deploy configs.
- [x] **M1 Content backbone** — models, Django Admin (Unfold), Cedar Hollow fixture, read-only endpoints, printable QR sheet.
- [x] **M2 Scan loop** — guest sessions, `POST /scan`, discovery XP once per animal, level-ups, marker landing, Welcome, Success, Profile, Choose Adventure, in-app scanner.
- [ ] **M3 Quests and challenges** — six verifiers, submit/hint, quest screens.
- [ ] **M4 Progression** — levels, badge rule engine, full Success sequence, Map.
- [ ] **M5 Hardening** — service worker, retries, throttling, analytics view.
- [ ] **M6 Field test.**

## Conventions

- Game numbers are never literals in code. Defaults live in `ZOOQUEST_DEFAULTS` (settings) and are overridden per zoo in `Zoo.settings`.
- Every content and play model has a `zoo` foreign key. Query through `.for_zoo(zoo)`.
- The frontend renders state; the API decides rules. If the browser knows the right answer, something is wrong.
- Fonts are self-hosted (`apps/web/src/fonts/`). No third-party requests from the explorer app at run time.
