from pyrogram import Client, filters
from database import get_role

Roles = {
    9: "العضو",  # أقل صلاحية
    8: "المميز",  # أقل صلاحية
    7: "ادمن",
    6: "المدير",
    5: "المنشئ",
    4: "المنشئ أساسي",
    3: "المالك",
    2: "المالك أساسي",
    1: "المطور",  # أعلى صلاحية
    0: "المطور الاساسي"  # أعلى صلاحية
}


# keyboard = InlineKeyboardMarkup([InlineKeyboardButton("تعديل الصلاحيات", callback_data="m1")])
#
#
# @Client.on_message(filters.group & filters.regex("^رفع مشرف$"))
# async def Prmotemoshref(client, message):
#     await message.reply_text(
#         "• صلاحيات المستخدم -", reply_markup=keyboard
#     )

@Client.on_message(filters.group & filters.regex("^رتبتي$"))
async def MyRank(client, message):
    sender = message.from_user
    chat = message.chat
    role = get_role(chat.id, sender.id)
    await message.reply_text(
        f"رتبتك هي **{Roles.get(role)}**",
    )
