import asyncio
import mimetypes
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from tqdm import tqdm


load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")


def load_telegram_config():
    api_id_value = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone = os.environ.get("TELEGRAM_PHONE")

    if not api_id_value or not api_hash or not phone:
        raise RuntimeError(
            "Set TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE before running."
        )

    return int(api_id_value), api_hash, phone


api_id, api_hash, phone = load_telegram_config()

client = TelegramClient("downloader_session", api_id, api_hash)

# Create folders
os.makedirs("Videos", exist_ok=True)
os.makedirs("PDFs", exist_ok=True)
os.makedirs("Images", exist_ok=True)

def progress_callback(current, total):
    progress_bar.update(current - progress_bar.n)


def infer_extension(message):
    if message.photo:
        return "jpg"

    mime_type = getattr(message.file, "mime_type", None) if message.file else None
    if mime_type:
        guessed = mimetypes.guess_extension(mime_type)
        if guessed:
            return guessed.lstrip(".")

        if mime_type.startswith("image/"):
            subtype = mime_type.split("/", 1)[1]
            return "jpg" if subtype == "jpeg" else subtype

        if mime_type == "application/pdf":
            return "pdf"

        if mime_type.startswith("video/"):
            return "mp4"

    if message.video:
        return "mp4"

    if message.document and message.file and message.file.ext:
        return message.file.ext.lstrip(".")

    return "bin"

async def main():
    print("Connecting to Telegram...")
    try:
        await asyncio.wait_for(client.start(phone=phone), timeout=30)
    except asyncio.TimeoutError:
        print("❌ Telegram connection timed out after 30 seconds. Check network access and try again.")
        return

    print("✅ Logged in successfully!")
    print("Paste links one by one. Type 'quit' to stop.\n")

    while True:
        link = input("Enter Telegram link (or 'quit'): ").strip()
        
        if link.lower() in ['quit', 'exit', 'q']:
            print("👋 Stopping downloader...")
            break
            
        # Normalize input: remove surrounding quotes and whitespace
        link_clean = link.strip().strip('"').strip("'")

        # Parse t.me / telegram.me URL like https://t.me/channel/12345
        m = re.search(r"(?:https?://)?(?:t\.me|telegram\.me)/(?P<channel>[^/]+)/(?P<id>\d+)", link_clean)

        try:
            if m:
                channel = m.group('channel')
                msg_id = int(m.group('id'))
                entity = await client.get_entity(channel)
                message = await client.get_messages(entity, ids=msg_id)
                # get_messages may return a list
                if isinstance(message, (list, tuple)):
                    message = message[0] if message else None
            else:
                # Fallback: try direct get_messages (IDs, usernames, etc.)
                message = await client.get_messages(link_clean)
            
            if not message or not message.media:
                print("❌ No media found or message inaccessible.\n")
                continue

            # Determine file name
            if message.file and message.file.name:
                filename = message.file.name
            else:
                ext = infer_extension(message)
                filename = f"telegram_{message.id}.{ext}"

            # Determine folder
            if message.video or (message.document and any(isinstance(attr, DocumentAttributeVideo) for attr in message.document.attributes)):
                folder = "Videos"
            elif message.photo or (message.file and message.file.mime_type and message.file.mime_type.startswith("image/")):
                folder = "Images"
            elif message.file and message.file.mime_type == "application/pdf":
                folder = "PDFs"
            else:
                folder = "."  # Other files in current folder

            filepath = os.path.join(folder, filename)
            
            print(f"📥 Downloading: {filename} → {folder}/")
            
            # Progress bar
            global progress_bar
            progress_bar = tqdm(total=message.file.size, unit='B', unit_scale=True, desc="Progress")
            
            await client.download_media(
                message,
                file=filepath,
                progress_callback=progress_callback
            )
            
            progress_bar.close()
            print(f"✅ Successfully saved: {filepath}\n")
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
            if 'progress_bar' in globals():
                progress_bar.close()

asyncio.run(main())