from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("{ رفع الادمنية }", callback_data="m1"),
            InlineKeyboardButton("{ تعطيل كل الاوامر }", callback_data="m1")
        ],
        [InlineKeyboardButton("{ مطور السورس }", callback_data="m1")],
    ],
)


@Client.on_message(filters.group & filters.regex("^تفعيل$"))
async def tf3eel(client, message):
    bot = await client.get_me()
    chat = message.chat
    # نجيب اخر صورة بروفايل للبوت
    photos = [p async for p in client.get_chat_photos(bot.id, limit=1)]
    caption_text = (
        "•الجروب :"+ chat.title + "\n"
        "• تم تفعيلها مسبقا"


    )

    if photos:
        await message.reply_photo(
            photo=photos[0].file_id,
            caption=caption_text,
            reply_markup=keyboard
        )
    else:
        await message.reply_text(
            caption_text,
            reply_markup=keyboard
        )
