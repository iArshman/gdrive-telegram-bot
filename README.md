# 🚀 GDRIVE TELEGRAM BOT

Professional Telegram Bot for Google Drive Management

## Features

- **Multiple Drive Accounts** – Connect and manage unlimited Google Drive accounts
- **File Browser** – Browse files and folders with intuitive navigation
- **File Upload** – Upload files from Telegram directly to Drive
- **File Download** – Download files from Drive to Telegram
- **Search** – Search across all your files quickly
- **Storage Info** – Monitor your Drive storage usage
- **File Operations** – Delete files, open folders, organize content
- **Backup Account** – Set a secondary Drive account as an automatic backup destination
- **Pyrogram / MTProto Support** – Bypass Bot API file size limits (up to 2 GB uploads & downloads)
- 


## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot / register or login |
| `/files` | Browse your Drive files |
| `/upload` | Upload a file from Telegram |
| `/search` | Search files |
| `/storage` | View storage information |
| `/addaccount` | Add a Google Drive account |
| `/settings` | Manage accounts & backup settings |
| `/logout` | Logout |

## Usage

1. **Connect Drive** – Use `/addaccount` to link your Google Drive
2. **Browse Files** – Use `/files` to navigate files and folders
3. **Upload** – Use `/upload` and send any file
4. **Download** – Click **⬇️ Download** on any file
5. **Search** – Use `/search` and type your query
6. **Share** – Click **🔗 Share** to get a public link
7. **Backup Account** – Open `/settings`, tap **Set Backup Account**, and enter the email of another linked Drive; toggle it on/off anytime

## Quick Start

### Prerequisites

- Python 3.9+
- MongoDB
- Telegram Bot Token
- Google Cloud Project with Drive API enabled (only for `internal` OAuth mode)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/iarshman/gdrive-telegram-bot
   cd gdrive-telegram-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

### Environment Variables

```env
# ── Bot ──────────────────────────────────────────────────────────────────────
BOT_TOKEN=your_telegram_bot_token

# ── Pyrogram / MTProto (https://my.telegram.org/apps) ────────────────────────
# Optional — enables uploads/downloads up to 2 GB
API_ID=your_api_id
API_HASH=your_api_hash

# ── Google OAuth ──────────────────────────────────────────────────────────────
# Required only when OAUTH_MODE=internal
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
REDIRECT_URI=https://your-domain.com/oauth_callback


# ── MongoDB ───────────────────────────────────────────────────────────────────
MONGO_URI=mongodb://localhost:27017

# ── Web Server 

PORT=3000

#
```

### File Size Limits

| Mode | Upload | Download |
|------|--------|----------|
| Standard Bot API | 20 MB | 50 MB |
| Pyrogram / MTProto (`API_ID` + `API_HASH` set) | 2 GB | 2 GB |


### Google Cloud Setup (internal OAuth mode only)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Drive API
3. Create OAuth 2.0 credentials (Web application)
4. Add authorized redirect URI: `https://your-domain.com/oauth_callback`
5. Configure OAuth consent screen with Drive scopes

---



---


## Deployment

Works with:
- Docker
- Any VPS with Python 3.9+

### Docker

```bash
docker build -t gdrive-telegram-bot .
docker run --env-file .env gdrive-telegram-bot
```

See `Dockerfile` for the full image definition.

## Security

- OAuth tokens encrypted in MongoDB
- HTTPS required for OAuth callbacks (when using web server mode)
- File content never stored permanently
- Users control all file operations
- Pyrogram session strings stored securely per-user in MongoDB


## License

MIT License

## Support

For issues and questions, open an issue on GitHub.

---

**Made with ❤️ for seamless Drive management**
