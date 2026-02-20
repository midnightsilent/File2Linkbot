import asyncio
import base64
import logging
from telethon import TelegramClient, events

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = ""
API_HASH = ""
BOT_TOKEN = ""
BOT_USERNAME = ""

LINK_PREFIX = f"https://t.me/{BOT_USERNAME}?start="

bot = TelegramClient("file_share_bot", API_ID, API_HASH)


def encode_payload(chat_id: int, message_id: int) -> str:

    raw = f"{chat_id}:{message_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def decode_payload(encoded: str) -> tuple[int, int]:

    padding = 4 - len(encoded) % 4
    if padding != 4:
        encoded += "=" * padding
    raw = base64.urlsafe_b64decode(encoded.encode()).decode()
    chat_id_str, message_id_str = raw.split(":")
    return int(chat_id_str), int(message_id_str)


@bot.on(events.NewMessage(pattern=r"/start ?(.*)"))
async def start_handler(event):
    args = event.pattern_match.group(1).strip()

    if not args:
        await event.respond(
            "سلام\n\n"
            "لطفا یک فایل بفرستید یا لینک دانلود را ارسال کنید\n"
        )
        return

    try:
        chat_id, message_id = decode_payload(args)
    except Exception:
        await event.respond("لینک نامعتبر است")
        return

    status_msg = await event.respond("در حال ارسال فایل...")

    try:
        await bot.forward_messages(
            entity=event.chat_id,
            messages=message_id,
            from_peer=chat_id,
            drop_author=True,
        )
        await status_msg.delete()
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        await event.respond(
            "خطا در ارسال فایل\n"
            "ممکنه فایل قدیمی باشه یا پیام اصلی حذف شده باشه"
        )


@bot.on(events.NewMessage(func=lambda e: e.is_private and e.media is not None and not e.text.startswith("/")))
async def file_handler(event):
    chat_id = event.chat_id
    message_id = event.id

    encoded = encode_payload(chat_id, message_id)
    link = f"{LINK_PREFIX}{encoded}"

    await event.reply(
        f"لینک فایل شما:\n\n"
        f"`{link}`\n\n"
    )


async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("OK. Bot is running...")
    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())