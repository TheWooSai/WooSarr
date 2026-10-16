# Backup & Restore

This document explains how to backup and restore WooSarr data.

## Backup

WooSarr stores all data in the `/config` directory. To backup your data:

```bash
tar -czf woosarr-backup.tar.gz /path/to/config
```

This will create a compressed backup of your entire configuration, including:
- Database (user data, mappings, exemptions)
- Secrets (Plex token, Discord token, master key)
- Logs

### Regular Backups

We recommend setting up regular backups using cron or a similar scheduler:

```bash
0 2 * * * tar -czf /backups/woosarr-$(date +\%Y\%m\%d).tar.gz /path/to/config
```

This will create a daily backup at 2 AM.

## Restore

To restore from a backup:

```bash
tar -xzf woosarr-backup.tar.gz -C /
```

This will restore the entire `/config` directory.

### Restore Specific Files

If you only need to restore specific files:

```bash
tar -xzf woosarr-backup.tar.gz /path/to/config/secrets/master.key
```

## Secret Key Handling

The master key (`/config/secrets/master.key`) is used to encrypt your secrets (Plex token, Discord token). If you lose this key, you will need to re-enter your secrets.

### Backing Up the Master Key

We recommend backing up the master key separately from the rest of the configuration:

```bash
cp /path/to/config/secrets/master.key /secure/backup/location/
```

### Losing the Master Key

If you lose the master key:
1. Re-enter your Plex token and Discord token in the web UI.
2. WooSarr will generate a new master key.
3. Your previous secrets will be re-encrypted with the new key.

## Disaster Recovery

In the event of a complete failure:
1. Restore the `/config` directory from backup.
2. Start the WooSarr container.
3. Verify that your mappings and exemptions are intact.