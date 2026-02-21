from pyrogram import Client
from pyrogram import idle
from database import init_db
import asyncio

bot = Client(
    "SecurityBot",
    api_id=17490746,
    api_hash="ed923c3d59d699018e79254c6f8b6671",
    bot_token="8579308846:AAGIAJFgkqr5z1S-XQPcbJj8vVQITcqbcLg",
    plugins=dict(root="plugins")
)


async def start_bot():
    print("[INFO]: جاري تشغيل البوت")
    await bot.start()
    init_db()
    # await bot.send_message(OWNER, "**≭︰تم تشغيل البوت **")
    await idle()


loop = asyncio.get_event_loop()
loop.run_until_complete(start_bot())
