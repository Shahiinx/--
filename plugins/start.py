from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from database import check_group

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("{ رفع الادمنية }", callback_data="prmoteadmins"),
            InlineKeyboardButton("{ تعطيل كل الاوامر }", callback_data="m1")
        ],
        [InlineKeyboardButton("{ مطور السورس }", url="https://t.me/X_Y_3")],
    ],
)


@Client.on_message(filters.group & filters.regex("^تفعيل$"))
async def tf3eel(client, message):
    bot = await client.get_me()
    chat = message.chat
    text = check_group(chat.id)
    # نجيب اخر صورة بروفايل للبوت
    photos = [p async for p in client.get_chat_photos(bot.id, limit=1)]
    caption_text = (
            "**•الجروب **: {" + chat.title + "}\n\n"
                                       f"**{text}**\n"

    )

    if photos:
        if text == "• تم تفعيلها مسبقا":
            await message.reply_photo(
                photo=photos[0].file_id,
                caption=caption_text,
                # reply_markup=keyboard
            )
        else:
            await message.reply_photo(
                photo=photos[0].file_id,
                caption=caption_text,
                reply_markup=keyboard
            )
    else:
        if text == "• تم تفعيلها مسبقا":
            await message.reply_text(
                caption_text,
                # reply_markup=keyboard
            )
        else:
            await message.reply_text(
                caption_text,
                reply_markup=keyboard

            )


@Client.on_callback_query(filters.regex("^prmoteadmins$"))
async def raise_admins(client, callback):
    chat_id = callback.message.chat.id


    # جلب كل أعضاء الجروب الحاليين
    async for member in client.get_chat_members(chat_id):
        if member.status in ["administrator", "creator"]:
            # حدد رتبة داخلياً: مالك = 3 أو مالك أساسي = 2، والباقي ادمن = 7
            if member.status == "creator":
                rank = 2  # مالك أساسي
            else:
                rank = 7  # ادمن
            set_role(chat_id, member.user.id, rank)

    await callback.answer("تم رفع الادمنية و المالكين ")
