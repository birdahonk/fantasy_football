
# Yahoo Fantasy Sports API — Fix Plan & Implementation Guide (v1.0)

**Goal:** Replace OAuth 1.0a with OAuth 2.0 (Authorization Code + Refresh tokens), eliminate rate-limit errors during auth, improve request/response handling, and stabilize the analyzer scripts.

---

## TL;DR (What to change right now)

1. **Migrate to OAuth 2.0 (Authorization Code flow, with PKCE if public app).**  
   Use Yahoo Identity’s OAuth 2 endpoints:  
   - **Authorize:** `https://api.login.yahoo.com/oauth2/request_auth`  
   - **Token:** `https://api.login.yahoo.com/oauth2/get_token`  
   - **Scopes:** `fspt-r` (read) or `fspt-w` (read/write), plus `profile email` if needed.

2. **Stop calling the OAuth 1.0a `get_request_token` endpoint.**  
   Your logs show `429 rate limited` from `oauth/v2/get_request_token` (OAuth 1.0a) and a misleading “✅ SUCCESS!” message even on failure. Remove 1.0a code and fix the success path.

3. **Add exponential backoff + jitter for *all* non-200 auth responses (esp. 429).**  
   First retry ≥ 60s, then 120s, 240s, 480s, capped at 15m. Persist last attempt time to avoid rapid re-runs.

4. **Return JSON from the Fantasy API to simplify parsing.**  
   Add `?format=json` (or `params={'format':'json'}`) and optionally `Accept: application/json`. Yahoo still defaults to XML; JSON is supported and widely used by wrappers.

5. **Store and refresh tokens.**  
   Save `access_token`, `refresh_token`, `expires_at`, `scope`, `token_type`. Auto-refresh before expiry using `/oauth2/get_token` with `grant_type=refresh_token`.

6. **Fix logging/messages.**  
   Don’t print “SUCCESS” on non-200. Include `status_code`, a truncated body, and the endpoint. Write API telemetry to `logs/api_calls.log` (you already do this).

7. **Update the NFL week helper for 2025 (and beyond).**  
   Your `utils.get_current_nfl_week()` is hard-coded for 2024. Make start date configurable or read from schedule; otherwise set the 2025 kickoff (e.g., first Thursday of Sept).

8. **Sanity-check config paths.**  
   First-run warning `config/yahoo_tokens.json not found` is fine; ensure it’s created after the first successful token exchange.

---

## Findings From Your Files

### 1) `yahoo_connect.py`
- Implements **OAuth 1.0a** (`oauth/v2/get_request_token`, `request_auth`, `get_token`) with HMAC-SHA1 and `oauth_callback='oob'`. This is the source of your rate-limit errors and unnecessary complexity.
- `make_request(...)` builds URLs like `https://fantasysports.yahooapis.com/fantasy/v2/{endpoint}` and parses **XML** via `xml_parser.py`. No `format=json` used.
- Logs show misleading success (“✅ SUCCESS! Request token: None”) after 429 failures — fix the success predicate.
- Token persistence only stores `access_token`, `access_secret`, `session_handle` (1.0a concepts).

### 2) `utils.py`
- Good: `log_api_call`, `ensure_directories`, and config helpers.
- Needs: Update `get_current_nfl_week()` (currently anchored to **2024-09-05**), and consider a central `User-Agent` + `timeout` defaults.

### 3) `xml_parser.py`
- Solid start for XML, but JSON eliminates this entire layer and makes downstream analyzers simpler. You can keep it for legacy fallbacks if you like.

### 4) Analyzer scripts (`main_analyzer.py`, `roster_analyzer.py`, `free_agent_analyzer.py`, `matchup_analyzer.py`, `performance_tracker.py`)
- They import `YahooFantasyAPI` and rely on its public methods. If you keep those method names & return structures stable, you can swap the internals to OAuth 2.0 + JSON with minimal analyzer changes.

---

## Recommended Architecture (OAuth 2.0)

### A. App Registration (Yahoo Developer)
- Register your app and set an **exact** Redirect URI (e.g., `http://127.0.0.1:8787/callback` for local dev). This must match your authorize request.  
- Scopes: `fspt-r` for read-only; `fspt-w` for read/write; add `profile email` only if required.

### B. Client Configuration
- Environment vars:
  ```bash
  # Provided
  export YAHOO_CLIENT_ID="<your client id>"

  # Add these (do NOT commit secrets)
  export YAHOO_CLIENT_SECRET="...only if using a confidential server app..."
  export YAHOO_REDIRECT_URI="http://127.0.0.1:8787/callback"
  export YAHOO_SCOPES="fspt-r"   # or fspt-w
  ```

- If you’re a native/desktop app, prefer **PKCE** and omit the client secret. If you’re a server web app, use the secret (no PKCE).

### C. OAuth 2.0 Flow
1. **Authorize URL** (open in browser):
   ```
   GET https://api.login.yahoo.com/oauth2/request_auth
     ?client_id=...&redirect_uri=...&response_type=code
     &scope=fspt-r%20profile%20email
     &state=STATE123
     # with PKCE: &code_challenge=...&code_challenge_method=S256
   ```
2. **Token Exchange**:
   ```
   POST https://api.login.yahoo.com/oauth2/get_token
   grant_type=authorization_code
   code=...&redirect_uri=...&client_id=...
   # with secret (server): include client_secret
   # with PKCE: include code_verifier
   ```
3. **Refresh**:
   ```
   POST https://api.login.yahoo.com/oauth2/get_token
   grant_type=refresh_token
   refresh_token=...&client_id=...
   # server: include client_secret
   ```
   Save `access_token`, `refresh_token`, `expires_in` → compute `expires_at`. Refresh proactively.

---

## HTTP Requests to Fantasy API

- Base: `https://fantasysports.yahooapis.com/fantasy/v2`
- Add `?format=json` (preferred) or keep XML (legacy).  
- **Auth header:** `Authorization: Bearer {access_token}` (OAuth 2.0).  
- Typical example (user games/leagues):
  ```
  GET /users;use_login=1/games;game_keys=nfl/leagues?format=json
  Host: fantasysports.yahooapis.com
  Authorization: Bearer ACCESS_TOKEN
  ```

---

## Concrete Code Tasks (file-by-file)

### `yahoo_connect.py` (major)
1. **Remove 1.0a code paths**: `_get_request_token`, `_generate_oauth_signature`, `_get_oauth_headers`, and any HMAC-SHA1 bits.
2. **Add OAuth2 client** (inline or new module `oauth2_client.py`):  
   - `start_authorization()` → builds request_auth URL (with PKCE for native) and opens browser or returns URL to the CLI.  
   - `exchange_code_for_tokens(code)` → POST to `/oauth2/get_token`.  
   - `refresh_tokens_if_needed()` → handles refresh.  
   - Persist to `config/yahoo_tokens.json`:
     ```json
     {
       "access_token": "...",
       "refresh_token": "...",
       "token_type": "Bearer",
       "scope": "fspt-r",
       "expires_at": 1699999999
     }
     ```
3. **Bearer auth for API calls**:  
   - `make_request(endpoint, method='GET', params=None)` should set headers:  
     `{'Authorization': f'Bearer {access_token}', 'User-Agent': 'YouvGotta/1.0', 'Accept': 'application/json'}`  
     Append `params={'format':'json'}` unless overridden.
4. **Retry policy**:  
   - On `429`, backoff with jitter (60s → 120s → 240s → 480s; cap 15m).  
   - On `401` + body/error that indicates expired token, call `refresh_tokens_if_needed()` once and retry.
5. **Return shape**: Preserve `{ 'status': 'success', 'data': raw_text_or_json, 'parsed': parsed_object }`. If using JSON, set both `data` (raw text) and `parsed` (dict).

### `utils.py` (minor)
- Add `get_http_session()` to centralize `timeout`, `User-Agent`, and maybe a small global rate limiter (sleep a few hundred ms between calls).
- Update `get_current_nfl_week()` to read from a config (e.g., `config/nfl_2025.json`) or at least bump the start date to 2025 and make it overridable via env var (`NFL_SEASON_START=2025-09-04`).
- Keep `log_api_call(...)` as-is; include `method` and `league/team` context if handy.

### `xml_parser.py` (optional going forward)
- If you switch to JSON, you can:  
  - Keep this file as a fallback, or  
  - Replace with a thin `json_normalize` helper for specific resources.

### Analyzer files
- Since they depend on `YahooFantasyAPI` methods, they should remain unchanged if we keep return contracts stable.  
- Consider adding lightweight input validation and clear exceptions when a required league/team key is missing.

### `safe_api_test.py`
- Keep the basic connectivity check, but clarify messages:  
  - 401 is expected *without* Bearer token.  
  - Add a small JSON check using a public-ish endpoint + `?format=json` just to confirm content-type handling.
- Do **not** attempt any OAuth here; this file should never trigger rate limits.

---

## Testing & Verification Steps

1. **Config sanity**: Ensure `YAHOO_CLIENT_ID` is set (you provided this), plus redirect URI and scopes.
2. **Manual Auth (first run)**:  
   - Run a CLI command that prints the authorize URL.  
   - Login to Yahoo, approve scopes, receive `code` at redirect.  
   - Paste `code` back; verify tokens written to `config/yahoo_tokens.json`.
3. **Make a simple API call**:  
   - `GET users;use_login=1/games;game_keys=nfl/leagues?format=json` → should return 200 with JSON.  
4. **Expire the token artificially** (set expires_at in the past) → next call should **auto-refresh** and succeed.  
5. **429 simulation**: Temporarily force your code to treat `429` as returned; verify exponential backoff path and correct logging.

---

## Observed Issues From Your Runtime Logs (and their fixes)

- **401 on fantasy endpoint** — expected without auth; confirms connectivity.  
- **429 on `get_request_token`** — you’re hitting a deprecated/legacy OAuth 1.0a endpoint repeatedly. **Fix**: Move to OAuth 2.0 flow, one call to `/oauth2/get_token` for code exchange, and then use refresh.  
- **“✅ SUCCESS! Request token: None”** — misleading success branch. **Fix**: Only print success when `status==200` and required fields parse (`oauth_token` no longer applies under OAuth2).  
- **Missing config on first run** — expected; after first auth, write `config/yahoo_tokens.json` with full token set.

---

## Ready-to-Assign Tasks for Your AI Coding Agent

1. **Refactor `yahoo_connect.py` to OAuth 2.0** (Authorization Code + PKCE for native):  
   - Remove 1.0a code; add bearer auth; add token persistence & refresh.
2. **Switch to JSON** for responses (`params['format']='json'`, `Accept: 'application/json'`); keep return contract stable.
3. **Implement backoff + jitter** for 429 and network errors; refresh-on-401.
4. **Tighten logging** (no false “SUCCESS”; add method + endpoint + truncated body previews).
5. **Update `utils.get_current_nfl_week()`** to be season-agnostic or 2025-ready.
6. **Improve `safe_api_test.py` messages** and ensure it never calls auth endpoints.
7. **Document `.env`** keys (ID, SECRET if applicable, REDIRECT_URI, SCOPES); never commit secrets.
8. **Smoke tests**: first-run auth, token refresh, simple data calls (games/leagues/teams).

---

### Appendix: Example Authorize URL (local dev)
```
https://api.login.yahoo.com/oauth2/request_auth
?client_id=YOUR_CLIENT_ID
&redirect_uri=http%3A%2F%2F127.0.0.1%3A8787%2Fcallback
&response_type=code
&scope=fspt-r%20profile%20email
&state=STATE123
# with PKCE:
&code_challenge=BASE64URL_SHA256(code_verifier)
&code_challenge_method=S256
```

If you want, I can also produce a drop-in `oauth2_client.py` with PKCE helpers and a small local callback server for the first-run authorization.
