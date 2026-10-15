#!/usr/bin/env python3
"""
Spike: Test Plex library sharing write operations.
Run with: python spikes/plex_write_test.py
Requires: PLEX_TOKEN environment variable
"""

import os
import sys

try:
    from plexapi.myplex import MyPlexAccount
except ImportError:
    print("plexapi not installed. Run: pip install plexapi")
    sys.exit(1)


def main():
    token = os.environ.get("PLEX_TOKEN")
    if not token:
        print("Set PLEX_TOKEN environment variable")
        return

    print("Connecting to Plex...")
    account = MyPlexAccount(token=token)
    print(f"Logged in as: {account.friendlyName} (id: {account.id})")

    # List servers
    print("\n--- Servers ---")
    servers = account.servers()
    print(f"Servers: {len(servers)}")
    for server in servers:
        print(f"  - {server.name} (id: {server.id})")

    # List friends
    print("\n--- Friends ---")
    friends = account.friends()
    print(f"Friends: {len(friends)}")
    for friend in friends:
        print(f"  - {friend.title} (id: {friend.id})")

    # Test updateFriend (dry run)
    if len(servers) > 0 and len(friends) > 0:
        server = servers[0]
        friend = friends[0]
        print("\n--- Dry Run: updateFriend ---")
        print(f"Would update friend {friend.title} (id: {friend.id})")
        print(f"on server {server.name} (id: {server.id})")
        print("To actually test, uncomment the updateFriend call below.")
        # account.updateFriend(friend.id, server.id, library_section_ids=[])
        print("Dry run complete.")


if __name__ == "__main__":
    main()
