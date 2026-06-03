# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BK-ITSM (蓝鲸流程服务) is a Vue 3 IT Service Management application. This is the **PC frontend** located at `frontend/pc/`.

## Commands

```bash
npm install          # Install dependencies
npm run dev          # Start Vite dev server (port 8004)
npm run build        # Production build (outputs to ../../../static/)
npm run build:production:sourcemap  # Production build with source maps
npm run preview      # Preview production build locally
npm run lint         # ESLint with auto-fix on src/
```

### Dev Server Setup

The dev server is configured via Vite env vars (`VITE_DEV_HOST`, `VITE_DEV_PORT`, `VITE_SET_URL`) — set these in `frontend/pc/.env.local` or similar. The server binds to `dev.{HOST}`:8004, so add a hosts entry like `127.0.0.1 dev.localhost`. The proxy forwards `/api/*`, `/openapi/*`, `/core/` to the backend.

## Architecture

### Entry & Initialization

`src/main.js` bootstraps Vue 3 with Vuex 4, Vue Router 4, and vue-i18n. Before mount, it dispatches `getPlatformPreData` (hits `init/` API). It globally registers UI components. Build system is **Vite 6** with `@vitejs/plugin-vue`. Static asset paths are managed via Vite's `base` config.

### Routing

- **Mode:** hash (`#` in URLs)
- **Modules:** `src/router/modules/` — `common.js`, `workbench.js`, `project.js`, `manage.js`
- **Key routes:** `/ticket` (ticket management), `/process` (process design), `/operation/data` (analytics), system config routes

### State Management

Single Vuex 4 store at `src/store/index.js` with ~40 namespaced modules in `src/store/modules/`. A separate `src/store/newModules/` contains `taskFlow`, `trigger`, and `user` modules. Root state holds `user`, `language`, `platformInfo`, `openFunction` (feature flags), and utility functions.

### API Layer

There is no separate `src/api/` directory. All API calls live inside Vuex store module actions, using the shared axios instance from `src/utils/ajax.js`.

**`src/utils/ajax.js`** configures:
- Base URL: `${window.SITE_URL}api/`
- CSRF token from cookie on every request
- Auth token from sessionStorage for ticket requests
- Response interceptors for 401 (login modal), 403 (permission denied), 499 (apply flow), 502 (app deployed)

### Components

- `src/components/common/` — shared components (layout, navigation, modals, exceptions)
- `src/components/renderview/` — dynamic form rendering framework
- `src/components/RenderField/` — dynamic form field renderers
- `src/components/form/` — form building blocks (tree select, rich text, advanced search)
- `src/components/ticket/` — ticket-specific components (approval dialog, export, evaluation)

### i18n

Three locales: `zh-cn` (default), `en`, `ja`. Language packs in `src/i18n/lang/`. Language determined by `blueking_language` cookie.

### Key Libraries

| Purpose | Library |
|---|---|
| UI | bk-magic-vue + Element UI |
| Flow design | jsplumb |
| Code editors | monaco-editor, brace (Ace) |
| Charts | @blueking/bkcharts |
| Rich text | wangeditor, @toast-ui/vue-editor |
| Drag & drop | vuedraggable |

## Code Conventions

- **Indent:** 2 spaces
- **`no-var` / `prefer-const`** enforced
- **`vue/order-in-components: error`** — components must follow the specified property order
- **Line endings:** LF (unix)
- **ESLint config:** extends `eslint-config-tencent` + `plugin:vue/recommended`
- **Component names:** PascalCase for route components, kebab-case in templates
- Node.js >= 16.0.0 required

## Production Build Notes

- Build tool: Vite 6 + `@vitejs/plugin-vue`
- Output goes to `../../../static/`
- `window.SITE_URL` controls API path prefix
- `window.BK_STATIC_URL` controls static asset path prefix
