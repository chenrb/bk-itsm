# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BK-ITSM (蓝鲸流程服务) is an IT Service Management application. Backend is Python 3.13 / Django 6.0 with DRF; frontend is Vue 3 (PC). It uses an embedded flow engine (`pipeline/`) for workflow orchestration and Celery for async tasks. The project has been fully decoupled from the BlueKing PaaS platform — no `blueapps`, `blueking`, `adapter`, `iam` SDK, `esb`, `apigw_manager`, or `six` imports remain.

## Commands

### Backend

Use `.venv/Scripts/python` for all Python commands (virtual environment in project root).

```bash
pip install -r requirements.txt                # Install dependencies
.venv/Scripts/python manage.py runserver       # Dev server (requires MySQL + Redis + env vars)
.venv/Scripts/python manage.py migrate         # Run migrations
.venv/Scripts/python manage.py init_builtin_data                # Initialize built-in data (first deploy or after DB reset)
.venv/Scripts/python manage.py init_builtin_data --list         # List available init modules
.venv/Scripts/python manage.py init_builtin_data --app role     # Run specific module only
.venv/Scripts/python manage.py init_builtin_data --skip sla     # Skip specific module
.venv/Scripts/python manage.py check                            # System check
.venv/Scripts/python manage.py makemigrations                   # Generate migrations
```

### Testing

```bash
# Django test runner
python manage.py test itsm.tests                                              # All tests
python manage.py test itsm.tests.workflow.test_workflow                       # Single module
python manage.py test itsm.tests.workflow.test_workflow.TestWorkflow.test_create_workflow  # Single method

# pytest (pytest.ini configures DJANGO_SETTINGS_MODULE, --reuse-db)
pytest itsm/tests/workflow/test_workflow.py
```

### Linting & Formatting

```bash
flake8 .       # Lint (max-line-length 120, max-complexity 25)
black .        # Format (line length 100)
isort .        # Sort imports (line_length=100, known_third_party=rest_framework, known_django=django)
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

Copy `.env.example` to `.env` and edit. Redis and MySQL are both required.

```
APP_CODE=bk_itsm         SECRET_KEY=changeme-in-production
DEBUG=true
BROKER_URL=redis://localhost:6379/0
REDIS_HOST=localhost     REDIS_PORT=6379       REDIS_PASSWORD=    REDIS_DB=0
REDIS_MODE=single
MYSQL_NAME=bk_itsm      MYSQL_USER=root       MYSQL_PASSWORD=root
MYSQL_HOST=localhost     MYSQL_PORT=3306       MYSQL_TEST_NAME=bk_itsm_test
PLATFORM_API_BASE_URL=   # Optional: base URL for platform_client HTTP calls
```

See `.env.example` for the full list including email, monitoring, notification, and business config.

## Architecture

### Settings loading chain

```
settings.py (root)                    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
  └→ config/default import *          # from config.default import *
       ├→ config/apps.py              #   INSTALLED_APPS, MIDDLEWARE, AUTHENTICATION_BACKENDS
       ├→ config/celery.py            #   CELERY_IMPORTS, broker, serializer
       ├→ config/database.py          #   DATABASES (MySQL via mysqlclient), REDIS dict, DEFAULT_AUTO_FIELD
       ├→ config/logging.py           #   LOGGING
       ├→ config/web.py               #   TEMPLATES, STATIC_URL, Mako config
       ├→ config/i18n.py              #   LANGUAGES, LOCALE_PATHS
       ├→ config/pipeline.py          #   pipeline engine config + is_superuser permission check
       ├→ config/business.py          #   AUTO_TIMEOUT_MINUTES, business constants
       ├→ config/integrations.py      #   platform URLs, frontend URL, webhook, docs
       └→ config/monitoring.py        #   monitoring/sentry config
  └→ config/local_settings import *   # gitignored — use for personal overrides
```

`config/__init__.py` defines `celery_app`, `BASE_DIR`, `APP_CODE`, `SECRET_KEY`, `DEBUG`.

### Auth

Custom user model: `AUTH_USER_MODEL = "users.User"` defined in `itsm/component/users/models.py` (extends `AbstractBaseUser` + `PermissionsMixin`). Authentication backends: Django's `ModelBackend` + `openapi.authentication.backend.CustomUserBackend`. Custom middleware at the top of the stack: `UserLoginForbiddenMiddleware`, `ServiceSwitchCheck`, `ApiIgnoreCheck`.

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

Each app follows Django conventions: `models.py` (or `models/`), `views.py` (or `views/`), `serializers.py`, `urls.py`, `tasks.py`.

### API routing

`urls.py` (root) dispatches:
- `/admin/` → Django admin
- `/account/` → `itsm.component.users.urls` (login/auth)
- `/api/` → `itsm.api.v1`
- `/openapi/` → `itsm.api.open_v1`
- `/openapi/v2/` → `itsm.api.open_v2`
- `/monitor/` → `itsm.monitor.urls`
- `/eri/admin/` → `pipeline.contrib.engine_admin.urls` (pipeline engine admin)
- `/` → `itsm.sites.urls` (frontend entry points)

### Pipeline engine

`pipeline/` is an embedded workflow engine (local code, not a pip package). `itsm/pipeline_plugins/` registers custom components (`components/collections/`) and variables (`variables/collections/`). The pipeline engine has its own Celery config imported via `from pipeline.celery.settings import *`. Pipeline completion hooks into ticket lifecycle via `PIPELINE_END_HANDLER = "itsm.ticket.handlers.pipeline_end_handler"`.

### Shared libraries

- **`itsm/component/`** — Shared backend utilities: DRF mixins, middlewares, `platform_client/http.py` (requests-based HTTP client replacing old ESB SDK), constants, notification helpers, field definitions, user model
- **`common/`** — Cross-cutting utilities: Redis, logging, XSS filtering, encryption, Mako template helpers
- **`business_rules/`** — Local business rule engine (not BlueKing-related)

### Celery

Five task modules registered in `CELERY_IMPORTS`: `ticket`, `service`, `sla_engine`, `trigger`, `task`. Tasks use pickle serializer. `manage.py` applies eventlet/gevent monkey-patching when Celery is invoked with those workers. `celery_app` is initialized in `config/__init__.py`.

### Database

MySQL via mysqlclient. Test DB configured via `MYSQL_TEST_NAME`. Each app has its own `migrations/` directory.

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

GitHub Actions (`.github/workflows/django.yml`): Python 3.13 + MySQL + Redis → install deps → migrate → `coverage run manage.py test itsm.tests` → Codecov.

## Refactoring

Refactoring plans and history are in `docs/refactor/`. Phases 1–16 are complete — the project is fully decoupled from BlueKing PaaS with all dead code cleaned. Migration history was reset in P3 (single `0001_initial` per app) — existing databases must be dropped and recreated. When modifying code during refactoring, follow the rules in `docs/refactor/plan.md`: always clean unused imports, dead dependencies, and stale config after deleting code.
