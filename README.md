# Telegram Content Downloader

A small utility to download media from Telegram messages. Supports:

- Single-message downloads (interactive): paste a Telegram message link and download immediately.
- Queue-based downloads: paste multiple links and download them in batch (two queue scripts provided).
- Private/restricted channels: the scripts can download media from private or restricted channels provided the authenticated Telegram account has access to those channels.

Warning: downloading media from channels you do not have permission to access may violate Telegram's terms of service or the channel owner's policies. Use this tool only with accounts that are authorized to view the content.

## Features

- Downloads videos and PDFs to separate folders (`Videos/`, `PDFs/`).
- Shows a progress bar while downloading large files.
- Uses `Telethon` for authenticated Telegram access — works with private/restricted channels if your account is a member and authenticated.
- Three entry points:
	- `script.py` — interactive single-link downloader.
	- `que_script.py` — queue-first downloader; type `start` to begin.
	- `queue_script.py` — queue-first downloader; type `done` or press Enter on an empty line to begin.

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy the example env file and fill in your Telegram credentials:

```bash
cp .env.example .env
# then edit .env and set TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
```

## Run

Run the script you want:

```bash
# interactive single link
python script.py

# queue then start (type 'start')
python que_script.py

# queue until 'done' or blank line, then download
python queue_script.py
```

## Security

- Do not commit `.env` or any files containing credentials. `.gitignore` includes `.env` and session/media files.
- Rotate your `api_hash`/`api_id` if they were exposed.

## Notes

- Downloads require the authenticated account to have access to the source message (private/restricted channels are supported when you are a member).
- The project stores a Telethon session file (`downloader_session.session`) locally so you won't need to re-authenticate on every run; this file is ignored by `.gitignore`.

If you'd like, add a short example link (public) to demonstrate behavior in the README.