import asyncio
from telegram import Bot
import logging
from datetime import datetime
from decouple import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = config("BOT_TOKEN")
CHAT_ID = config("CHAT_ID")

order_messages = {}


async def send_telegram_message(message):
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error sending message: {e}")


def send_contact_notification(full_name, email, message):
    text = f"""📩 <b>Новое сообщение с сайта!</b>
    ━━━━━━━━━━━━━━━━━━━━━
    👤 <b>Имя:</b> {full_name}
    📧 <b>Email:</b> {email}
    📝 <b>Сообщение:</b>
    <pre>{message}</pre>
    ━━━━━━━━━━━━━━━━━━━━━
    ⏰ <b>Дата:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_telegram_message(text))
    loop.close()
