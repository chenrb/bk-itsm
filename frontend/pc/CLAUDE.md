# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BK-ITSM (蓝鲸流程服务) is a Vue 2 IT Service Management application built on the BlueKing platform. This is the **PC frontend** located at `frontend/pc/`. A sibling WeChat frontend exists at `frontend/weixin/`.

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

The dev server requires local hosts configuration. Edit `vite.config.js` to set `HOST` and `SET_URL`, then add a hosts entry like `127.0.0.1 dev.paas.bking.com`. The proxy forwards `/api/*`, `/openapi/*`, `/core/`, and `/sops/*` to the backend.

## Architecture

### Entry & Initialization

`src/main.js` bootstraps Vue with Vuex, Router, and vue-i18n. Before mount, it dispatches `getPlatformPreData` (hits `init/` API). It globally registers **bk-magic-vue** (primary UI library) and selected **Element UI** components. Build system is **Vite** with `vite-plugin-vue2`. Static asset paths are managed via Vite's `base` config.

### Routing

- **Mode:** hash (`#` in URLs)
- **Base path:** managed by `@blueking/sub-saas` for sub-app integration; iframe routes use empty base
- **Modules:** `src/router/modules/` — `common.js`, `workbench.js`, `project.js`, `manage.js`
- **Key routes:** `/ticket` (ticket management), `/process` (process design), `/operation/data` (analytics), system config routes

### State Management

Single Vuex store at `src/store/index.js` with ~40 namespaced modules in `src/store/modules/`. A separate `src/store/newModules/` contains `taskFlow`, `trigger`, and `user` modules. Root state holds `user`, `language`, `platformInfo`, `openFunction` (feature flags), and utility functions.

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

Three locales: `zh-cn` (default), `en`, `ja`. Language packs in `src/i18n/lang/`. Language determined by `blueking_language` cookie. Both bk-magic-vue and Element UI locales are configured separately.

### Key Libraries

| Purpose | Library |
|---|---|
| UI | bk-magic-vue 2.5 + Element UI 2.4 |
| Flow design | jsplumb |
| Code editors | monaco-editor, brace (Ace) |
| Charts | @blueking/bkcharts |
| Rich text | wangeditor, @toast-ui/vue-editor |
| Drag & drop | vuedraggable |
| Platform integration | @blueking/sub-saas, @blueking/platform-config |

## Code Conventions

- **Indent:** 2 spaces (tabs in Prettier config, but ESLint enforces 2-space indent for JS/Vue)
- **Quotes:** double quotes in HTML attributes, no strict enforcement in JS
- **Semicolons:** used but `no-extra-semi` enforced
- **`no-var` / `prefer-const`** enforced
- **`camelcase: off`** — backend API fields are often snake_case, so camelCase is not enforced on variables
- **`vue/order-in-components: error`** — components must follow the specified property order
- **`vue/no-v-html: off`** — v-html is allowed
- **Line endings:** LF (unix)
- **Max line length:** effectively 120 (not enforced as error)
- **ESLint config:** extends `eslint-config-tencent` + `plugin:vue/recommended`
- **Component names:** PascalCase for route components, kebab-case in templates

## Production Build Notes

- Build tool: Vite 4 + `vite-plugin-vue2`
- Output goes to `../../../static/` (three levels up from `frontend/pc/`)
- `window.SITE_URL` controls API path prefix
- `window.BK_STATIC_URL` controls static asset path prefix
- Node.js >= 16.0.0 required
