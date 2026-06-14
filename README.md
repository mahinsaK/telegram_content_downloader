# Telegram Content Downloader

A small utility to download media from Telegram messages. It supports
single-link interactive downloads and queue-based batch downloads. The
scripts use Telethon for authenticated access and can download media
from private/restricted channels when the authenticated account has
permission.

**Capabilities**
- Single-message interactive downloader (`script.py`).
- Queue-based batch downloaders (`que_script.py`, `queue_script.py`).
- Saves media into `Videos/` and `PDFs/` and displays a progress bar.

**Quick Setup**
1. Create and activate a Python virtual environment and install deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

2. Copy the example env file and populate your Telegram credentials locally:

```bash
cp .env.example .env
# edit .env and set TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
```

**How to get `TELEGRAM_API_ID` / `TELEGRAM_API_HASH`**
1. Visit https://my.telegram.org and sign in with your Telegram account.
2. Open "API development tools" and create a new application.
3. Copy the provided `api_id` (numeric) and `api_hash` (string) into your
	 local `.env` file. Keep `api_hash` secret.

**Run**

```bash
# Interactive single link
python script.py

# Queue mode (type 'start' to begin or 'done' to finish depending on script)
python que_script.py
python queue_script.py
```

**Notes & Security**
- The authenticated Telegram account must have access to any private or
	restricted channels you want to download from.
- Do not commit `.env` or any files containing credentials. The
	repository includes `.env.example` and `.gitignore` already ignores
	`.env` and session/media files.

For examples or questions, open an issue in the repository.