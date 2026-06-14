# Telegram Video Downloader

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For a new machine or another person, copy the template first:

```bash
cp .env.example .env
```

## Run

Put your Telegram credentials in the local `.env` file in the project root:

```bash
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+your_phone_number
```

Then start the script:

```bash
python script.py
```

To queue multiple links first and download them after you type `start`, use:

```bash
python que_script.py
```

The queue script lets you paste one Telegram link per line, then type `start` to begin downloads. Type `quit` to exit without downloading.

If you want to queue multiple links first and download them after, run:

```bash
python queue_script.py
```

In `queue_script.py`, paste one link per line, then type `done` or press Enter on a blank line to start downloading.

## Verify isolation

```bash
which python
which pip
python -c "import sys; print(sys.prefix)"
```

All three should point inside `.venv`.