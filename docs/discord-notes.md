# Discord API Verification Notes (P0-05)

**Date:** 2026-10-15
**Library:** discord.py v2.4.0

## Slash Commands

### Registration

Slash commands are registered using the `@bot.tree.command()` decorator:

```python
from discord.ext import commands
import discord

bot = commands.Bot(command_prefix="!")
tree = bot.tree

@tree.command(name="link", description="Link your Plex account")
async def link(interaction: discord.Interaction, plex_username: str):
    await interaction.response.send_message(f"Linked {plex_username}")

# Sync commands to Discord
await tree.sync()
```

### Command Options

```python
@tree.command(name="grant", description="Grant library access")
async def grant(
    interaction: discord.Interaction,
    user: discord.Member,
    library: str
):
    await interaction.response.send_message(f"Granted {library} to {user.name}")
```

### Rate Limits

- Global: 5 requests per second
- Per-endpoint: Varies (see Discord docs)
- Slash command registration: Limited, sync once at startup

## Privileged Intents

### MEMBERS Intent

Required for:

- Getting guild members
- Getting member roles
- Tracking role changes

```python
intents = discord.Intents.default()
intents.members = True  # Privileged intent

bot = commands.Bot(command_prefix="!", intents=intents)
```

### Requirements

- Bots in < 100 servers: Enable in Developer Portal
- Bots in ≥ 100 servers: Requires verification
- WooSarr use case: Single guild, no verification needed

## Event Handling

### Role Changes

```python
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        # Role changed, trigger sync
        pass
```

### Member Join/Leave

```python
@bot.event
async def on_member_join(member):
    # New member joined
    pass

@bot.event
async def on_member_remove(member):
    # Member left
    pass
```

## Verification Result

✅ **VERIFIED:** discord.py supports all required features:

- Slash commands with options
- Privileged intents (MEMBERS)
- Role change event handling
- Member join/leave events

## Notes

- Use `tree.sync()` to register slash commands
- MEMBERS intent is required for role tracking
- Rate limits are generous for single-guild use
