# Yahoo Fantasy Sports OAuth2 – Analysis & Recommendations

## Issue
Your OAuth2 flow is currently returning:

```
error=invalid_scope&error_description=invalid+scope
```

This happens because the requested scope is not valid for Yahoo Fantasy Sports.

---

## Correct Scopes
- **`fspt-r`** → Read-only access (rosters, standings, league settings, stats, etc.).
- **`fspt-w`** → Read/write access (required for transactions like adds, drops, lineup/position changes, trades).

> ✅ Recommendation: Use `fspt-w` if your app will execute **adds/drops or position changes**.  
> ✅ Use `fspt-r` if you only need read-only queries.

---

## Required Changes

### 1. Scope
Set scope to one of the following in your request URL:

```text
scope=fspt-r
```
or
```text
scope=fspt-w
```

Do not include `openid`, `email`, or `profile` unless explicitly needed.

---

### 2. Token Request Headers
In `oauth2_client.py`, update the token exchange headers.  
**Current (incorrect):**
```python
headers = {
    'Content-Type': 'application/xaml+xml, application/xml, text/xml, */*',
    'User-Agent': 'FantasyFootballApp/1.0'
}
```

**Fix (correct):**
```python
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'FantasyFootballApp/1.0'
}
```

---

### 3. Example Authorization URL
```text
https://api.login.yahoo.com/oauth2/request_auth
  ?client_id=YOUR_CLIENT_ID
  &redirect_uri=YOUR_REDIRECT_URI
  &response_type=code
  &scope=fspt-w
  &state=fantasy_football_app
```

---

### 4. Example API Call After Token Exchange
```http
GET https://fantasysports.yahooapis.com/fantasy/v2/users;use_login=1/games
Authorization: Bearer <access_token>
```

---

## Next Steps
1. Update scope to `fspt-w` (if you need transactions).  
2. Fix `Content-Type` header.  
3. Re-run flow and test with a basic Fantasy Sports API endpoint.  
4. Add a transaction test call once tokens are working.

---
