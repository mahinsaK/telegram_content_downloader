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

### How to get `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`

1. Open https://my.telegram.org in a browser and sign in with your Telegram phone number.
2. Click "API development tools" (or "Create new application").
3. Enter an application title and short name (URL and platform fields are optional) and submit.
4. After creation you'll see the numeric `api_id` and the `api_hash` string — copy those values.
5. Add them to your local `.env` as `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`. Keep `api_hash` secret and do not commit it to source control.

Note: you will also need to authenticate with your phone number the first time you run the scripts; Telethon will send a login code to that number and then store an authenticated session file locally.

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