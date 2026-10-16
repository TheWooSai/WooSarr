# Sync Rules

This document explains how WooSarr syncs Plex library access with Discord roles.

## Basic Sync

WooSarr maps Discord roles to Plex libraries. When a user's Discord roles change, WooSarr automatically updates their Plex library access.

### Additive Sync

By default, WooSarr uses additive sync. This means:
- When a user gains a Discord role, they are granted access to the mapped Plex library.
- When a user loses a Discord role, they are removed from the mapped Plex library.

### Exemptions

You can exempt specific users from automatic sync. Exempted users keep their current library access regardless of role changes.

To add an exemption:
1. Go to the Exemptions page in the web UI.
2. Select the user and library to exempt.
3. Save the exemption.

### Manual Grants

You can manually grant library access to users without requiring a Discord role. Manual grants are not affected by automatic sync.

To add a manual grant:
1. Go to the Manual Grants page in the web UI.
2. Select the user and library to grant access to.
3. Save the grant.

### External Shares

WooSarr can also manage external Plex shares. When a user is granted access to a library, WooSarr can automatically create an external share for them.

To enable external shares:
1. Go to the Settings page in the web UI.
2. Enable "Manage External Shares".
3. Save the settings.

## Sync Triggers

WooSarr syncs automatically when:
- A Discord role change is detected (via Discord webhook).
- A manual sync is triggered from the web UI.
- The container starts (initial sync).

## Conflict Resolution

When there are conflicts between automatic sync and manual grants/exemptions, the following priority is used:
1. Exemptions (highest priority)
2. Manual Grants
3. Automatic Sync (lowest priority)

This means that if a user is exempted from a library, they will keep their access even if they lose the corresponding Discord role. If a user has a manual grant, they will keep their access even if they lose the corresponding Discord role.