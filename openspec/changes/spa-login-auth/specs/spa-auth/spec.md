## ADDED Requirements

### Requirement: Login page renders at /login route
The system SHALL provide a Vue SPA login page at the `/login` route with username and password fields. The page SHALL NOT display the main navigation sidebar.

#### Scenario: Unauthenticated user opens the app
- **WHEN** a user opens the application without a valid session
- **THEN** the system redirects to the `/login` route and displays the login form

#### Scenario: Login page has no navigation
- **WHEN** the login page is displayed
- **THEN** the main navigation component (sidebar, header) is hidden

### Requirement: Login via JSON API
The system SHALL accept login credentials as JSON body (`username`, `password`) via `POST /account/login/` and return a JSON response. The endpoint SHALL enforce CSRF protection.

#### Scenario: Successful login
- **WHEN** user submits valid username and password
- **THEN** Django creates a session, returns `{"result": true, "data": {"username": "..."}}`, and sets `itsm_sessionid` cookie

#### Scenario: Failed login
- **WHEN** user submits invalid credentials
- **THEN** the system returns `{"result": false, "message": "用户名或密码错误"}` with HTTP 401

#### Scenario: CSRF token required
- **WHEN** POST request is sent without valid `X-CSRFToken` header
- **THEN** Django returns HTTP 403 (CSRF verification failed)

### Requirement: CSRF cookie provision
The system SHALL set the `itsm_csrftoken` cookie on responses that may be accessed before authentication (e.g., `GET /init/`, `GET /account/login/`).

#### Scenario: Unauthenticated init request sets CSRF cookie
- **WHEN** an unauthenticated user sends `GET /init/`
- **THEN** the response includes the `Set-Cookie: itsm_csrftoken=...` header and returns HTTP 401

### Requirement: Init endpoint returns 401 for unauthenticated users
The `GET /init/` endpoint SHALL return HTTP 401 with `{"result": false, "message": "未登录", "code": 401}` when no valid session exists.

#### Scenario: Anonymous user calls init
- **WHEN** a request reaches `/init/` without a valid `itsm_sessionid` cookie
- **THEN** the response status is 401 and body contains `{"result": false, "message": "未登录"}`

#### Scenario: Authenticated user calls init
- **WHEN** a request reaches `/init/` with a valid session
- **THEN** the response status is 200 and body contains user data (username, chname, permissions, etc.)

### Requirement: Router guard enforces authentication
The Vue router SHALL redirect unauthenticated users to `/login` and prevent authenticated users from accessing the login page.

#### Scenario: Unauthenticated user navigates to protected route
- **WHEN** `window.username` is falsy and user navigates to any route except `/login`
- **THEN** router redirects to `/login`

#### Scenario: Authenticated user navigates to /login
- **WHEN** `window.username` is truthy and user navigates to `/login`
- **THEN** router redirects to `/`

### Requirement: 401 responses redirect to login
All API 401 responses SHALL trigger navigation to the `/login` route, both during app initialization and after mount.

#### Scenario: 401 during app initialization
- **WHEN** the `GET /init/` call returns 401 before Vue app mounts
- **THEN** the app still mounts and router guard redirects to `/login`

#### Scenario: 401 after app is mounted
- **WHEN** any API call returns 401 after the app is running
- **THEN** `window.location.hash` is set to `#/login`

### Requirement: Logout clears state and redirects to login
The system SHALL provide logout via `POST /account/logout/` and clear all frontend authentication state.

#### Scenario: User clicks logout
- **WHEN** user triggers logout
- **THEN** a POST request is sent to `/account/logout/`, `window.username` and related globals are cleared, and router navigates to `/login`

### Requirement: Cookie names use itsm_ prefix
The system SHALL use `itsm_sessionid` for session cookie and `itsm_csrftoken` for CSRF cookie.

#### Scenario: Login sets itsm_ prefixed cookies
- **WHEN** user successfully authenticates
- **THEN** browser receives `itsm_sessionid` and `itsm_csrftoken` cookies

### Requirement: Language cookie uses itsm_language
The system SHALL use `itsm_language` as the language preference cookie name instead of `blueking_language`.

#### Scenario: Language detection reads itsm_language
- **WHEN** the application initializes or language-related code reads the language preference
- **THEN** it reads from the `itsm_language` cookie

### Requirement: BlueKing SSO code is removed
All BlueKing SSO related code SHALL be removed from the codebase, including `@blueking/login-modal` dependency, `login.js`, `isCrossOriginIFrame.js`, `passApi.js`, `login_success.html`, and `UserLoginForbiddenMiddleware`.

#### Scenario: No BlueKing SSO imports remain
- **WHEN** searching the frontend source for `showLoginModal`, `BLUEKING`, `bk-gloabal`, `login_url`, `login_success`
- **THEN** no matches are found
