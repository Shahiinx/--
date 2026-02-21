import os
import sys
import importlib
from pyrogram import Client, filters
from config import OWNER

@Client.on_message(filters.command("reload") & filters.user(OWNER))
async def restart_bot(client, message):
    await message.reply("♻️ جاري إعادة تشغيل البوت...")
    os.execl(sys.executable, sys.executable, *sys.argv)