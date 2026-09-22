# SEO Score API

Hosted REST API that crawls a URL, runs modular SEO checks, and returns a 0–100 report.

**Current stage: 1 — Project scaffold** (API process, Postgres, Redis, health check). No crawler yet.

## Why this stage exists

Before we score anyone’s site, we need a place to store users, API keys, audits, and usage. This stage proves the database, Redis, and HTTP server start and talk to each other.

Python mapping from the original Node spec:

| Spec | This repo |
|---|---|
| Fastify | FastAPI |
| Prisma | SQLAlchemy 2 + Alembic |
| BullMQ | ARQ (Stage 4) |
| Playwright | Playwright for Python (Stage 2) |

The check-module contract lives in `src/seo_score/engine/types.py`. New checks register themselves; scoring reads YAML weights in `config/scoring.yaml`.

## Local setup

Requires Docker Desktop (Postgres + Redis) and Python 3.12+.

```bash
cd seo-score-api
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

docker compose up -d
alembic upgrade head
uvicorn seo_score.api.main:app --reload --port 8000
```

In another terminal:

```bash
curl -s http://127.0.0.1:8000/health
# expect: {"status":"ok","version":"0.1.0","postgres":"ok","redis":"ok"}
```

Unit tests (do not require Docker):

```bash
pytest tests/test_engine_contract.py -q
```

Health integration (requires Compose running):

```bash
pytest tests/test_health.py -q
```

## Accounts you will need later

Nothing for Stage 1.

- **Stage 3:** [PageSpeed Insights API key](https://developers.google.com/speed/docs/insights/v5/get-started)
- **Stage 7:** Stripe account + four prices
- **Deploy:** Railway or Fly.io
