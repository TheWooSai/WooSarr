# WooSarr

Plex ↔ Discord Role Library Sync

A single Docker container that automatically grants/removes Plex library access for Plex users based on their Discord roles.

## Features

- OAuth authentication with Plex (no stored credentials)
- Discord bot integration for role-based access control
- Web UI for configuration and management
- Automatic sync on role changes
- Manual library grants and exemptions
- Detailed logging and audit trail

## Installation

### Docker

```bash
docker run -d \
  --name woosarr \
  -p 2000:2000 \
  -v /path/to/config:/config \
  ghcr.io/thewoosai/woosarr:latest
```

### Unraid

Add the WooSarr template to your Unraid installation:

1. Go to Docker → Add Container
2. Enter the template URL: `https://github.com/TheWooSai/WooSarr/raw/main/unraid/woosarr.xml`
3. Configure the container settings
4. Start the container

## Configuration

After starting the container, navigate to `http://your-server:2000` to access the web UI.

### First-Run Walkthrough

1. **Setup Discord Bot**: Create a Discord application, add a bot, and copy the token.
2. **Setup Plex Integration**: Sign in with Plex OAuth and select your server.
3. **Configure Mappings**: Map Discord roles to Plex libraries.
4. **Start Syncing**: Enable automatic sync to keep access in sync.

### Reverse Proxy / HTTPS

Port 2000 is HTTP by default. For production use, we recommend placing WooSarr behind a reverse proxy with HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name woosarr.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:2000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## FAQ

**Q: What happens if I lose my master key?**
A: You will need to re-enter your secrets (Plex token, Discord token). The master key encrypts these secrets in the database.

**Q: Can I grant access to a user without a Discord role?**
A: Yes, you can use manual grants to give access to specific users.

**Q: Can I exempt a user from automatic sync?**
A: Yes, you can add exemptions to prevent automatic role changes for specific users.

**Q: How often does WooSarr sync?**
A: WooSarr syncs automatically when Discord role changes are detected. You can also trigger a manual sync from the web UI.

## Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## License

MIT