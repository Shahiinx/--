from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from config import OWNER
import time


@Client.on_message(filters.group & filters.regex(r"^المطور$"))
async def ShowCommands(client, message):
    dev = await client.get_chat(OWNER[0])

    # نجيب اخر صورة بروفايل
    photos = [p async for p in client.get_chat_photos(dev.id, limit=1)]

    if photos:
        file_id = photos[0].file_id

        await message.reply_photo(
            photo=file_id,
            caption=(
                "**الـمـطـور الاسـاسـي**\n\n"
                f"◉𝚍𝚎𝚟 𝚗𝚊𝚖𝚎 : {dev.first_name}\n"
                f"◉𝚍𝚎𝚟 𝚞𝚜𝚎𝚛 : ❲@{dev.username}❳\n"
                f"◉𝚍𝚎𝚟 𝚒𝚍 : ❲{dev.id}❳\n"
                f"◉𝚋𝚒𝚘 ⚘ : ❲{dev.bio or '-'}❳"
            ),

        )
    else:
        await message.reply_text(
            "**الـمـطـور الاسـاسـي**\n\n"
            f"◉𝚍𝚎𝚟 𝚗𝚊𝚖𝚎 : {dev.first_name}\n"
            f"◉𝚍𝚎𝚟 𝚞𝚜𝚎𝚛 : ❲@{dev.username}❳\n"
            f"◉𝚍𝚎𝚟 𝚒𝚍 : ❲{dev.id}❳\n"
            f"◉𝚋𝚒𝚘 ⚘ : ❲{dev.bio or '-'}❳"
        )
    sender = message.from_user  # أو dev لو عندك مطور محدد
    chat = message.chat

    # تحديد رابط الشات
    if chat.username:
        chat_link = f"https://t.me/{chat.username}"
    else:
        chat_id = str(chat.id).replace("-100", "")
        chat_link = f"https://t.me/c/{chat_id}/{message.id}"


    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(sender.first_name, url=f"https://t.me/{sender.username or f'tg://user?id={sender.id}'}")],
        [InlineKeyboardButton(f"{chat.title}", url=chat_link)]

    ])

    await client.send_message(
        chat_id=sender.id,  # أو dev.id لو عندك آيدي المطور
        text=(
            "●  مرحباً عزيزي المطور\n"
            "شخص ما يحتاج الي مساعده\n"
            # "⩹━━━━َِ𝐑𝐙 • 𝐒𝐎𝐔𝐑𝐂𝐄,━━━━⩺\n"
            f"●  اسمه :- {sender.first_name}\n"
            f"●  ايديه :- {sender.id}\n"
            f"●  - معرفة @{sender.username or '-'}"
        ),
        reply_markup=keyboard
    )