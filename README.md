# SEO Score API

A REST API that takes a URL, crawls it, runs a series of automated SEO checks against the page, and returns a score out of 100 along with a breakdown of what passed and what didn't.

The idea is simple: point it at any webpage, and instead of manually auditing title tags, meta descriptions, heading structure, page speed, and other on-page SEO factors, you get a single API call back with a clear score and the specifics behind it.

Each SEO check is built as a self-contained, pluggable module — so new checks can be added over time without touching the core scoring logic. Weights for how much each check contributes to the final score are configured separately, making the scoring model easy to tune.

## Tech stack

- **FastAPI** — HTTP API layer
- **PostgreSQL** — persistent storage (users, API keys, audit history)
- **Redis** — caching and job queueing
- **SQLAlchemy + Alembic** — ORM and database migrations
- **Docker Compose** — local Postgres + Redis
- **Playwright** — page crawling (added in a later stage)

## Getting started

### Requirements

- Docker Desktop
- Python 3.12+

### Setup

```bash
git clone <your-repo-url>
cd seo-score-api

# Set up environment variables
cp .env.example .env

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Start Postgres and Redis
docker compose up -d

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn seo_score.api.main:app --reload --port 8000
```

The API will be running at `http://127.0.0.1:8000`.

### Verify it's working

In a separate terminal:

```bash
curl -s http://127.0.0.1:8000/health
```

## Running tests

Unit tests only (no Docker needed):

```bash
pytest tests/test_engine_contract.py -q
```

Full integration tests (requires Postgres/Redis running via Docker):

```bash
pytest tests/test_health.py -q
```

## Project structure

```
src/seo_score/
├── api/          # FastAPI routes and app entrypoint
├── core/         # config and shared settings
├── db/           # database models and session handling
└── engine/       # SEO check modules and scoring logic

config/
└── scoring.yaml  # weights for each SEO check

alembic/          # database migrations
tests/            # unit and integration tests
```
