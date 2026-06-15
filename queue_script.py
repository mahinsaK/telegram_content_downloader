import asyncio
import mimetypes
import os
import re

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from tqdm import tqdm


load_dotenv()


def load_telegram_config():
    api_id_value = os.environ.get("TELEGRAM_API_ID")
    api_hash = os.environ.get("TELEGRAM_API_HASH")
    phone = os.environ.get("TELEGRAM_PHONE")

    if not api_id_value or not api_hash or not phone:
        raise RuntimeError(
            "Set TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE before running."
        )

    return int(api_id_value), api_hash, phone


def normalize_link(link: str) -> str:
    return link.strip().strip('"').strip("'").strip()


def parse_message_reference(link: str):
    link_clean = normalize_link(link)
    match = re.search(
        r"(?:https?://)?(?:t\.me|telegram\.me)/(?P<channel>[^/]+)/(?P<id>\d+)",
        link_clean,
    )
    if match:
        return match.group("channel"), int(match.group("id"))
    return None, None


def get_download_target(message):
    if message.file and message.file.name:
        filename = message.file.name
    else:
        mime_type = getattr(message.file, "mime_type", None) if message.file else None
        if message.photo:
            ext = "jpg"
        elif mime_type:
            guessed = mimetypes.guess_extension(mime_type)
            if guessed:
                ext = guessed.lstrip(".")
            elif mime_type.startswith("image/"):
                subtype = mime_type.split("/", 1)[1]
                ext = "jpg" if subtype == "jpeg" else subtype
            elif mime_type == "application/pdf":
                ext = "pdf"
            elif mime_type.startswith("video/"):
                ext = "mp4"
            elif message.video:
                ext = "mp4"
            else:
                ext = "bin"
        elif message.video:
            ext = "mp4"
        elif message.document:
            ext = "pdf"
        else:
            ext = "bin"
        filename = f"telegram_{message.id}.{ext}"

    if message.video or (
        message.document
        and any(isinstance(attr, DocumentAttributeVideo) for attr in message.document.attributes)
    ):
        folder = "Videos"
    elif message.photo or (
        message.file and message.file.mime_type and message.file.mime_type.startswith("image/")
    ):
        folder = "Images"
    elif message.file and message.file.mime_type == "application/pdf":
        folder = "PDFs"
    else:
        folder = "."

    return folder, filename, os.path.join(folder, filename)


def progress_callback(current, total):
    progress_bar.update(current - progress_bar.n)


async def resolve_message(client, link: str):
    link_clean = normalize_link(link)
    channel, msg_id = parse_message_reference(link_clean)

    if channel and msg_id:
        entity = await client.get_entity(channel)
        message = await client.get_messages(entity, ids=msg_id)
        if isinstance(message, (list, tuple)):
            message = message[0] if message else None
        return message

    return await client.get_messages(link_clean)


async def download_link(client, link: str):
    global progress_bar

    message = await resolve_message(client, link)

    if not message or not message.media:
        print(f"❌ No media found or message inaccessible: {link}")
        return

    folder, filename, filepath = get_download_target(message)

    os.makedirs(folder, exist_ok=True)
    print(f"📥 Downloading: {filename} → {folder}/")

    progress_bar = tqdm(total=message.file.size, unit="B", unit_scale=True, desc="Progress")

    try:
        await client.download_media(
            message,
            file=filepath,
            progress_callback=progress_callback,
        )
        print(f"✅ Successfully saved: {filepath}\n")
    finally:
        progress_bar.close()


async def main():
    api_id, api_hash, phone = load_telegram_config()
    client = TelegramClient("downloader_session", api_id, api_hash)

    await client.start(phone=phone)
    print("✅ Logged in successfully!")
    print("Paste multiple links, one per line. Type 'done' or press Enter on a blank line to start downloading. Type 'quit' to exit.\n")

    queue = []

    while True:
        link = input("Add link (or 'done'/'quit'): ").strip()

        if link.lower() in ["quit", "exit", "q"]:
            print("👋 Stopping downloader...")
            return

        if link.lower() == "done" or link == "":
            break

        queue.append(link)
        print(f"Queued {len(queue)} link(s).")

    if not queue:
        print("No links queued. Exiting.")
        return

    print(f"\nStarting downloads for {len(queue)} queued link(s)...\n")
    for index, link in enumerate(queue, start=1):
        print(f"[{index}/{len(queue)}] Processing: {link}")
        try:
            await download_link(client, link)
        except Exception as e:
            print(f"❌ Error for {link}: {e}\n")


asyncio.run(main())