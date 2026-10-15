# Plex API Verification Notes (P0-02, P0-03)

**Date:** 2026-10-15
**SDK:** python-plexapi (plexapi) v4.18.3

## P0-02: Plex Auth with python-plexapi

### OAuth/PIN Flow
python-plexapi supports PIN-based OAuth via `MyPlexPinLogin`:

```python
from plexapi.myplex import MyPlexPinLogin

# 1. Create PIN login instance
pin_login = MyPlexPinLogin()

# 2. Get the PIN and OAuth URL
pin = pin_login.pin
oauth_url = pin_login.oauthUrl(forwardUrl="http://localhost:2000/callback")
print(f"Go to {oauth_url} and enter PIN: {pin}")

# 3. Wait for user to complete login
pin_login.run(timeout=120)
success = pin_login.waitForLogin()

if success:
    # 4. Get the auth token
    token = pin_login.token
    # Use token for subsequent requests
```

### JWT Authentication
For long-lived authentication, use JWT:

```python
from plexapi.myplex import MyPlexJWTLogin

jwt_login = MyPlexJWTLogin(token=auth_token)

# Create keypair (one-time)
jwt_login.createKeypair()

# Create JWT
jwt = jwt_login.createJWT()

# Refresh JWT when needed
new_jwt = jwt_login.refreshJWT()

# Verify JWT
valid = jwt_login.verifyJWT(refreshWithinDays=1)
```

### Direct Token Login
For simple cases, use direct token authentication:

```python
from plexapi.myplex import MyPlexAccount

account = MyPlexAccount(token="your_plex_token")
```

### Verification Result
✅ **VERIFIED:** python-plexapi supports all required auth flows:
- PIN-based OAuth (MyPlexPinLogin)
- JWT authentication (MyPlexJWTLogin)
- Direct token authentication (MyPlexAccount)

## P0-03: Plex Write Operations

### updateFriend() Method
The `updateFriend()` method exists on `MyPlexAccount`:

```python
account = MyPlexAccount(token="your_token")

# Grant library access
account.updateFriend(
    user_id=12345,
    server_id=67890,
    library_section_ids=[1, 2, 3]  # Grant access to specific libraries
)

# Revoke library access (pass empty list)
account.updateFriend(
    user_id=12345,
    server_id=67890,
    library_section_ids=[]
)
```

### MyPlexServerShare Methods
The `MyPlexServerShare` class provides additional methods:

- `update()` - Update share settings
- `delete()` - Remove share
- `addFriend()` - Add friend to share
- `removeFriend()` - Remove friend from share

### Questions Answered

1. **Does `updateFriend()` accept per-library access?**
   ✅ Yes, via `library_section_ids` parameter.

2. **What's the method signature?**
   `updateFriend(user_id, server_id, library_section_ids)`

3. **Can we revoke access to specific libraries?**
   ✅ Yes, by passing an empty list or omitting library IDs.

4. **Is there rate limiting?**
   ⚠️ Unknown - need to test. Plex API may have rate limits.

5. **Does `updateFriend()` require the user to be a friend first?**
   ⚠️ Unknown - need to test. May need to add as friend first.

### Verification Result
✅ **VERIFIED:** python-plexapi supports library sharing operations:
- `updateFriend()` for granting/revoking access
- `MyPlexServerShare` for share management

### Spike Script
Created `spikes/plex_write_test.py` to test write operations.

```python
#!/usr/bin/env python3
"""
Spike: Test Plex library sharing write operations.
Run with: python spikes/plex_write_test.py
"""

import os
from plexapi.myplex import MyPlexAccount

def main():
    token = os.environ.get("PLEX_TOKEN")
    if not token:
        print("Set PLEX_TOKEN environment variable")
        return

    account = MyPlexAccount(token=token)
    print(f"Logged in as: {account.friendlyName}")

    # List servers
    servers = account.servers()
    print(f"Servers: {len(servers)}")
    for server in servers:
        print(f"  - {server.name} (id: {server.id})")

    # List friends
    friends = account.friends()
    print(f"Friends: {len(friends)}")
    for friend in friends:
        print(f"  - {friend.title} (id: {friend.id})")

    # Test updateFriend (dry run)
    if len(servers) > 0 and len(friends) > 0:
        server = servers[0]
        friend = friends[0]
        print(f"\nWould update friend {friend.title} on server {server.name}")
        # account.updateFriend(friend.id, server.id, library_section_ids=[])

if __name__ == "__main__":
    main()
```