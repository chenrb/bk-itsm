# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BK-ITSM (蓝鲸流程服务) is an IT Service Management application. Backend is Python 3.13 / Django 6.0 with DRF; frontend is Vue 3 (PC). It uses an embedded flow engine (`pipeline/`) for workflow orchestration and Celery for async tasks. The project has been fully decoupled from the BlueKing PaaS platform — no `blueapps`, `blueking`, `adapter`, `iam` SDK, `esb`, `apigw_manager`, or `six` imports remain.

## Commands

### Backend

```bash
pip install -r requirements.txt    # Install dependencies
python manage.py runserver         # Dev server (requires MySQL + Redis + env vars)
python manage.py migrate           # Run migrations
# Use .venv for all Python commands:
.venv/Scripts/python manage.py check       # System check
.venv/Scripts/python manage.py makemigrations  # Generate migrations
python manage.py test itsm.tests   # Run all tests (Django test runner)
python manage.py test itsm.tests.workflow.test_workflow                                    # Single module
python manage.py test itsm.tests.workflow.test_workflow.TestWorkflow.test_create_workflow  # Single method
pytest itsm/tests/workflow/test_workflow.py  # Alternative (pytest.ini config)
flake8 .          # Lint
black .           # Format
isort .           # Sort imports
```

### Frontend

```bash
cd frontend/pc
npm install
npm run dev          # Vite dev server on port 8004
npm run build        # Production build -> ../../../static/
npm run lint         # ESLint with auto-fix
```

### Pre-commit hooks

Configured in `.pre-commit-config.yaml`: black, flake8, commitlint. Install with:
```bash
pre-commit install && pre-commit install --hook-type commit-msg
```

## Environment Variables (local dev)

Set in `.env` or `config/local_settings.py`:

```
APP_CODE=bk_itsm         SECRET_KEY=changeme-in-production
RUN_VER=open             DEBUG=true
BROKER_URL=redis://localhost:6379/0
REDIS_HOST=localhost     REDIS_PORT=6379
MYSQL_NAME=bk_itsm      MYSQL_USER=root       MYSQL_PASSWORD=root
MYSQL_HOST=localhost     MYSQL_PORT=3306       MYSQL_TEST_NAME=bk_itsm_test
PLATFORM_API_BASE_URL=   # Optional: base URL for platform_client HTTP calls
```

## Architecture

### Settings loading

`settings.py` (root) is minimal — it installs pymysql, then does `from config.default import *`. `config/default.py` aggregates 10 sub-modules by concern:

```
config/apps.py         → INSTALLED_APPS, MIDDLEWARE, AUTHENTICATION_BACKENDS
config/celery.py       → CELERY_IMPORTS, broker, serializer
config/database.py     → DATABASES (MySQL via PyMySQL)
config/logging.py      → LOGGING
config/web.py          → TEMPLATES, STATIC_URL, etc.
config/i18n.py         → LANGUAGES, LOCALE_PATHS
config/pipeline.py     → pipeline engine config + is_superuser permission check
config/business.py     → AUTO_TIMEOUT_MINUTES, business constants
config/integrations.py → platform URLs (BK_CC_HOST, BK_JOB_HOST, etc.)
config/monitoring.py   → monitoring/sentry config
```

`config/local_settings.py` is gitignored — use it for personal overrides.

### Django apps (under `itsm/`)

| App | Role |
|-----|------|
| `workflow/` | Workflow definition and versioning (process designer) |
| `ticket/` | Ticket lifecycle; includes `schedule_monitor.py` (pipeline stuck-task auto-fix) |
| `service/` | Service catalog management |
| `trigger/` | Event trigger rules and actions |
| `task/` | Task management |
| `sla/` + `sla_engine/` | SLA policies and timing engine |
| `project/` | Project/workspace management |
| `role/` | Role-based access |
| `openapi/` | Public gateway API (v1, v2) |
| `postman/` | Third-party API management |
| `pipeline_plugins/` | Pipeline engine plugins (custom components + variables) |
| `gateway/` | External platform API wrappers |
| `meta/` | Metadata management |
| `iadmin/` | Admin configuration panel |
| `monitor/` | Prometheus monitoring endpoints |
| `misc/` | Miscellaneous utilities |

### API routing

`urls.py` (root) dispatches:
- `/api/` → `itsm.api.v1`
- `/openapi/` → `itsm.api.open_v1`
- `/openapi/v2/` → `itsm.api.open_v2`
- `/monitor/` → `itsm.monitor.urls`
- `/` → `itsm.sites.urls` (frontend entry points)

Each `itsm/` app follows Django conventions: `models.py` (or `models/`), `views.py` (or `views/`), `serializers.py`, `urls.py`, `tasks.py`.

### Pipeline engine

`pipeline/` is an embedded workflow engine (local code, not a pip package). `itsm/pipeline_plugins/` registers custom components (`components/collections/`) and variables (`variables/collections/`). The pipeline engine has its own Celery config imported via `from pipeline.celery.settings import *`.

### Shared libraries

- **`itsm/component/`** — Shared backend utilities: DRF mixins, middlewares, `platform_client/http.py` (requests-based HTTP client replacing old ESB SDK), constants, notification helpers, field definitions, user model
- **`common/`** — Cross-cutting utilities: Redis, logging, XSS filtering, encryption, Mako template helpers
- **`business_rules/`** — Local business rule engine (not BlueKing-related)

### Celery

Five task modules registered in `CELERY_IMPORTS`: `ticket`, `service`, `sla_engine`, `trigger`, `task`. Tasks use pickle serializer.

### Database

MySQL via PyMySQL. Test DB configured via `MYSQL_TEST_NAME`. Each app has its own `migrations/` directory.

### Templates

Mako templates in `mako_templates/` for error pages, service close page, and email notifications. Django templates in `templates/` for admin. Configured in `config/web.py`.

## Code Conventions

### Python

- **Python 3.13**, Django 6.0
- **Formatter:** black (line length 100)
- **Linter:** flake8 (max-line-length 120, max-complexity 25)
- **Import sorting:** isort (line_length=100, known_third_party=rest_framework, known_django=django)
- **Test files:** `test_*.py` pattern
- **No Python 2 compatibility code** — no `six`, no `__future__` imports needed

### Commit messages

Conventional commits enforced via commitlint: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `perf`, `chore`. Merge commits ignored.

### Frontend

See `frontend/pc/CLAUDE.md` for full Vue conventions. Key: Vue 3 + Vite 4 + Vuex 4, ESLint extends `eslint-config-tencent` + `plugin:vue/recommended`.

## CI

GitHub Actions (`.github/workflows/django.yml`): Python 3.13 + MySQL + Redis → install deps → migrate → `coverage run manage.py test itsm.tests` → Codecov upload.

## Refactoring

Refactoring plans and history are in `docs/refactor/`. Phase 1 (去蓝鲸依赖) and Phase 2 (死代码清理) are complete. P3 (迁移重置) has reset all migrations to a single `0001_initial` per app — existing databases must be dropped and recreated. When modifying code during refactoring, follow the rules in `docs/refactor/plan.md`: always clean unused imports, dead dependencies, and stale config after deleting code.

## Virtual Environment

Use `.venv` in the project root as the Python virtual environment. All `python` / `manage.py` commands should use `.venv/Scripts/python`.
