#!/bin/bash
set -e

# PUID/PGID support for Unraid
if [ -n "$PUID" ] || [ -n "$PGID" ]; then
    PUID=${PUID:-1000}
    PGID=${PGID:-1000}

    # Update group ID
    if getent group woosarr > /dev/null; then
        groupmod -g "$PGID" woosarr
    else
        groupadd -g "$PGID" woosarr
    fi

    # Update user ID
    if id woosarr > /dev/null; then
        usermod -u "$PUID" -g "$PGID" woosarr
    else
        useradd -u "$PUID" -g "$PGID" -m woosarr
    fi

    # Fix ownership
    chown -R "$PUID":"$PGID" /app /config
fi

# Run as non-root user
exec su-exec woosarr "$@"