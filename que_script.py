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


def ensure_output_folders():
    os.makedirs("Videos", exist_ok=True)
    os.makedirs("PDFs", exist_ok=True)
    os.makedirs("Images", exist_ok=True)


def parse_telegram_link(link_clean):
    return re.search(
        r"(?:https?://)?(?:t\.me|telegram\.me)/(?P<channel>[^/]+)/(?P<id>\d+)",
        link_clean,
    )


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


async def resolve_message(client, link_clean):
    match = parse_telegram_link(link_clean)

    if match:
        channel = match.group("channel")
        msg_id = int(match.group("id"))
        entity = await client.get_entity(channel)
        message = await client.get_messages(entity, ids=msg_id)
        if isinstance(message, (list, tuple)):
            message = message[0] if message else None
        return message

    return await client.get_messages(link_clean)


async def download_message(client, message, filepath):
    file_size = getattr(message.file, "size", None) or 0

    if file_size > 0:
        with tqdm(total=file_size, unit="B", unit_scale=True, desc="Progress") as progress_bar:

            def progress_callback(current, total):
                progress_bar.update(current - progress_bar.n)

            await client.download_media(
                message,
                file=filepath,
                progress_callback=progress_callback,
            )
    else:
        await client.download_media(message, file=filepath)


async def collect_links():
    print("Paste one or more Telegram links, one per line.")
    print("Type 'start' on a new line to begin downloading, or 'quit' to stop.\n")

    queued_links = []
    while True:
        link = input("Link: ").strip()

        if not link:
            continue

        if link.lower() in {"quit", "exit", "q"}:
            return []

        if link.lower() == "start":
            return queued_links

        queued_links.append(link.strip().strip('"').strip("'"))
        print(f"Queued {len(queued_links)} link(s).")


async def main():
    api_id, api_hash, phone = load_telegram_config()
    ensure_output_folders()

    client = TelegramClient("downloader_session", api_id, api_hash)
    await client.start(phone=phone)
    print("✅ Logged in successfully!\n")

    queued_links = await collect_links()
    if not queued_links:
        print("No links queued. Exiting.")
        return

    print(f"\nStarting download of {len(queued_links)} queued link(s).\n")

    for index, link in enumerate(queued_links, start=1):
        print(f"[{index}/{len(queued_links)}] Processing: {link}")

        try:
            message = await resolve_message(client, link)

            if not message or not message.media:
                print("❌ No media found or message inaccessible.\n")
                continue

            folder, filename, filepath = get_download_target(message)
            print(f"📥 Downloading: {filename} -> {folder}/")

            await download_message(client, message, filepath)

            print(f"✅ Successfully saved: {filepath}\n")

        except Exception as error:
            print(f"❌ Error: {error}\n")


if __name__ == "__main__":
    asyncio.run(main())