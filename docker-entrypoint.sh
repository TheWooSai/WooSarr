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

# Ensure config directories exist and have correct ownership
mkdir -p /config/secrets /config/logs
chown -R woosarr:woosarr /config

# Run as non-root user
exec su -s /bin/bash woosarr -c "$*"