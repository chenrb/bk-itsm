## 1. Backend: Cookie & Config

- [x] 1.1 Change CSRF cookie name from `bkitsm_csrftoken` to `itsm_csrftoken` in `config/web.py`
- [x] 1.2 Change session cookie name from `bkitsm_sessionid` to `itsm_sessionid` in `config/web.py`
- [x] 1.3 Rename `blueking_language` to `itsm_language` in `itsm/iadmin/views.py`

## 2. Backend: Login API

- [x] 2.1 Rewrite `LoginView` to function-based `login_view` accepting JSON body in `itsm/users/views/auth.py`
- [x] 2.2 Add `@ensure_csrf_cookie` and `@require_http_methods(["GET", "POST"])` decorators
- [x] 2.3 Update URL reference in `itsm/users/urls.py` from `LoginView.as_view()` to `login_view`
- [x] 2.4 Delete `templates/registration/login.html`

## 3. Backend: Init & Middleware

- [x] 3.1 Add authentication check to `init()` view — return 401 for anonymous users
- [x] 3.2 Remove `need_target` and `location` fields from init response
- [x] 3.3 Delete `UserLoginForbiddenMiddleware` class from `misc_middlewares.py`
- [x] 3.4 Remove `UserLoginForbiddenMiddleware` from MIDDLEWARE in `config/apps.py`
- [x] 3.5 Clean up unused `JsonResponse` import in `misc_middlewares.py`

## 4. Frontend: Login Page & Router

- [x] 4.1 Create `src/views/login/index.vue` with username/password form
- [x] 4.2 Add `/login` route with `meta: { noNav: true }` to router
- [x] 4.3 Add auth check to `router.beforeEach` guard
- [x] 4.4 Update `App.vue` to hide navigation on `noNav` routes

## 5. Frontend: Auth Flow Rewrite

- [x] 5.1 Remove `@blueking/login-modal` import and `showLoginModal` call from `ajax.js`
- [x] 5.2 Replace init 401 handler with `window.location.hash = '#/login'`
- [x] 5.3 Replace general 401 handler with `window.location.hash = '#/login'`
- [x] 5.4 Hardcode `xsrfCookieName: 'itsm_csrftoken'` in axios config
- [x] 5.5 Update `main.js`: remove `login.js` import, mount app even on init failure
- [x] 5.6 Remove `need_target` redirect logic from `store/index.js` and `stores/root.js`
- [x] 5.7 Rewrite logout in `Navigation.vue` to POST `/account/logout/` + clear state + router push

## 6. Frontend: Cleanup

- [x] 6.1 Delete `src/utils/login.js`
- [x] 6.2 Delete `src/utils/isCrossOriginIFrame.js`
- [x] 6.3 Delete `src/utils/passApi.js`
- [x] 6.4 Delete `login_success.html`
- [x] 6.5 Remove `@blueking/login-modal` from `package.json`
- [x] 6.6 Remove `window.login_url` and `window.BK_USER_MANAGE_HOST` from `index.html`
- [x] 6.7 Set default `window.username` to empty string in `index.html`
- [x] 6.8 Rename `blueking_language` to `itsm_language` in all frontend files (10 files)
- [x] 6.9 Remove `BK_USER_MANAGE_HOST` fallback in `memberSelect/index.vue`

## 7. Verification

- [x] 7.1 Django system check passes (`manage.py check`)
- [x] 7.2 Frontend build succeeds (`npm run build`)
- [x] 7.3 No remaining BK SSO references in frontend source
