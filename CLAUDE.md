# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BK-ITSM (蓝鲸流程服务) is an IT Service Management application built on the BlueKing platform. Backend is Python/Django 4.2 with DRF; frontend is Vue 2 (PC + WeChat). It uses a flow engine (`pipeline`) for workflow orchestration and Celery for async tasks.

## Commands

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server (requires MySQL + Redis + env vars, see .env example below)
python manage.py runserver

# Run migrations
python manage.py migrate

# Run all unit tests (Django test runner, targets itsm.tests)
python manage.py test itsm.tests

# Run a single test module
python manage.py test itsm.tests.workflow.test_workflow

# Run a single test class/method
python manage.py test itsm.tests.workflow.test_workflow.TestWorkflow.test_create_workflow

# Run with pytest (alternative, uses pytest.ini config)
pytest itsm/tests/workflow/test_workflow.py

# Lint with flake8
flake8 .

# Format with black
black .

# Sort imports
isort .
```

### Frontend (PC)

```bash
cd frontend/pc
npm install
npm run dev          # Dev server on port 8004
npm run build        # Production build -> ../../../static/
npm run lint         # ESLint with auto-fix
```

### Frontend (WeChat)

```bash
cd frontend/weixin
# Similar Vue 2 setup
```

### Pre-commit hooks

Configured in `.pre-commit-config.yaml`: black, flake8, commitlint. Install with `pre-commit install && pre-commit install --hook-type commit-msg`.

## Environment Variables (local dev)

Required env vars (set in `.env` or `config/local_settings.py`):

```
RUN_ENV=open
APP_CODE=bk_itsm
RUN_VER=open
SECRET_KEY=12345678-1234-5678-1234-123456789012
APP_TOKEN=12345678-1234-5678-1234-123456789012
BK_PAAS_HOST=http://127.0.0.1
BROKER_URL=redis://localhost:6379/0
USE_IAM=false
BKAPP_REDIS_HOST=localhost
BKAPP_REDIS_PORT=6379
BK_MYSQL_NAME=bk_itsm_ci
BK_MYSQL_USER=root
BK_MYSQL_PASSWORD=root
BK_MYSQL_HOST=localhost
BK_MYSQL_PORT=3306
BK_MYSQL_TEST_NAME=bk_itsm_ci_test
```

## Architecture

### Settings loading

`settings.py` is a loader — it detects the environment (`BKPAAS_ENVIRONMENT` or `BK_ENV`) and imports the corresponding config module:
- `config/dev.py` — local development (loads `config/local_settings.py` for personal overrides)
- `config/stag.py` — staging
- `config/prod.py` — production
- `config/default.py` — shared settings (INSTALLED_APPS, MIDDLEWARE, etc.)

Environment-specific overrides come from `adapter/config/sites/{RUN_VER}/` (e.g. `adapter/config/sites/open/`).

### Django apps (under `itsm/`)

The main business logic lives in Django apps under the `itsm/` package:

- **`itsm/workflow/`** — Workflow definition and versioning (the core process designer)
- **`itsm/ticket/`** — Ticket lifecycle management (create, state transitions, approval, comments)
- **`itsm/service/`** — Service catalog management
- **`itsm/trigger/`** — Event trigger rules and actions
- **`itsm/task/`** — Task management
- **`itsm/sla/`** / **`itsm/sla_engine/`** — SLA policies and timing engine
- **`itsm/project/`** — Project/workspace management
- **`itsm/role/`** — Role-based access
- **`itsm/openapi/`** — Public API (gateway-exposed)
- **`itsm/postman/`** — Third-party API management
- **`itsm/pipeline_plugins/`** — Pipeline engine plugins (custom components + variables)
- **`itsm/auth_iam/`** — IAM (identity access management) integration
- **`itsm/gateway/`** — Wrappers around external BlueKing platform APIs
- **`itsm/meta/`** — Metadata management
- **`itsm/notice/`** — Notification management
- **`itsm/misc/`** — Miscellaneous utilities
- **`itsm/iadmin/`** — Admin configuration panel
- **`itsm/helper/`** — Helper utilities (registered first in INSTALLED_APPS)
- **`itsm/monitor/`** — Prometheus monitoring endpoints

### API routing

URLs in `urls.py` dispatch to:
- `/api/` → `itsm.api.v1` — internal REST API
- `/openapi/` → `itsm.api.open_v1` — public gateway API v1
- `/openapi/v2/` → `itsm.api.open_v2` — public gateway API v2
- `/monitor/` → `itsm.monitor.urls` — Prometheus metrics

Each app under `itsm/` has its own `urls.py` and `views.py` (or `api.py`) following Django conventions.

### Pipeline engine

`pipeline/` is an embedded workflow engine (not the `pipeline` pip package — this is local). `itsm/pipeline_plugins/` registers custom components (`components/collections/`) and variables (`variables/collections/`) that the pipeline engine uses to execute workflow steps.

### Shared component libraries

- **`itsm/component/`** — Shared backend utilities: DRF mixins, middlewares, ESB/APiGW clients, decorators, constants, notification helpers, task utilities, field definitions
- **`common/`** — Cross-cutting utilities: Redis helpers, middleware, context processors, logging, encryption
- **`iam/`** — IAM SDK for permission evaluation
- **`adapter/`** — Environment-specific configuration adapters (sites/open, sites/ieod, etc.)
- **`blueking/`** — BlueKing platform API client SDK (CMDB, Job, etc.)

### Frontend architecture

PC frontend (`frontend/pc/`) and WeChat frontend (`frontend/weixin/`) are separate Vue 2 apps. See `frontend/pc/CLAUDE.md` for detailed frontend architecture.

### Celery

Four worker processes defined in `app_desc.yaml`:
- **web** — Gunicorn serving Django
- **beat** — Celery beat scheduler
- **pworker** — Prefork thread pool worker (concurrency 10)
- **gworker** — Gevent worker (concurrency 4)

Celery tasks live in `tasks.py` files within each app (e.g. `itsm/ticket/tasks.py`, `itsm/trigger/tasks.py`).

### Database

MySQL via PyMySQL. Migrations in each app's `migrations/` directory. Test database configured via `BK_MYSQL_TEST_NAME`.

## Code Conventions

### Python

- **Python 3.11**, Django 4.2
- **Formatter:** black (line length 100, from isort config)
- **Linter:** flake8 (max-line-length 120, max-complexity 25)
- **Import sorting:** isort (line_length=100, known_third_party=rest_framework, known_django=django)
- Test files match `test_*.py` pattern
- Each Django app follows: `models.py` / `models/`, `views.py` / `views/`, `serializers.py` / `serializers/`, `urls.py`, `tasks.py`

### Commit messages

Conventional commits enforced via commitlint: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `perf`, `chore`. Merge commits are ignored.

### Frontend

See `frontend/pc/CLAUDE.md` for full ESLint, formatting, and Vue conventions.

## CI

GitHub Actions workflow (`.github/workflows/django.yml`) runs on push/PR:
1. Sets up Python 3.11 + MySQL + Redis
2. Installs deps + runs migrations
3. Runs `coverage run manage.py test itsm.tests`
4. Uploads coverage to Codecov
