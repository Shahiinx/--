from pyrogram import Client, filters
from database import get_role, set_role, remove_role

# 0 أعلى رتبة — 9 أقل رتبة
Roles = {
    9: "عضو",
    8: "مميز",
    7: "ادمن",
    6: "مدير",
    5: "منشئ",
    4: "منشئ أساسي",
    3: "مالك",
    2: "مالك أساسي",
    1: "مطور",
    0: "مطور أساسي"
}

ROLE_COMMANDS = {
    "عضو": 9,
    "مميز": 8,
    "ادمن": 7,
    "مدير": 6,
    "منشئ": 5,
    "منشئ أساسي": 4,
    "مالك": 3,
    "مالك أساسي": 2,
    "مطور": 1,
    "مطور أساسي": 0
}


def normalize_role(role):
    return 9 if role is None else role


@Client.on_message(filters.group & filters.regex("^رتبتي$"))
async def my_rank(client, message):
    sender = message.from_user
    chat = message.chat

    role_level = normalize_role(get_role(chat.id, sender.id))
    role_name = Roles.get(role_level, "عضو")

    await message.reply_text(f"• رتبتك هي ← **{role_name}**")


@Client.on_message(filters.group & filters.regex(r"^(رفع|تنزيل) (.+)$"))
async def handle_roles(client, message):
    sender = message.from_user
    chat = message.chat
    text = message.text.strip()

    sender_role = normalize_role(get_role(chat.id, sender.id))

    parts = text.split()
    action = parts[0]

    if len(parts) < 2:
        return

    target_role_name = parts[1]
    target_role_level = ROLE_COMMANDS.get(target_role_name)

    # if target_role_level is None:
    #     await message.reply_text("⚠️ رتبة غير معروفة.")
    #     return

    target = None

    # الحالة 1: بالرد
    if message.reply_to_message:
        target = message.reply_to_message.from_user

    # الحالة 2: باليوزر
    elif len(parts) >= 3:
        username = parts[2].replace("@", "")
        try:
            target = await client.get_users(username)
        except:
            await message.reply_text("⚠️ لم يتم العثور على المستخدم.")
            return
    else:
        await message.reply_text("⚠️ لازم ترد على شخص أو تكتب يوزره.")
        return

    if not target:
        return

    # if target.id == sender.id:
    #     await message.reply_text("⚠️ لا يمكنك تعديل رتبتك بنفسك.")
    #     return

    target_current_role = normalize_role(get_role(chat.id, target.id))

    # حماية المطور الأساسي
    # if target_current_role == 0:
    #     await message.reply_text("⛔ لا يمكن تعديل رتبة المطور الأساسي.")
    #     return

    # ❗ الشرط الأساسي: لازم رتبتك أعلى من الهدف
    if sender_role >= target_current_role:
        await message.reply_text("⚠️ لا يمكنك تعديل شخص أعلى منك أو مساوي لك.")
        return

    # ❗ ولازم رتبتك أعلى من الرتبة الجديدة
    if sender_role >= target_role_level:
        await message.reply_text("⚠️ لا يمكنك منحه رتبة أعلى منك.")
        return

    # تنفيذ العملية
    if action == "رفع":
        set_role(chat.id, target.id, target_role_level)
        await message.reply_text(
            f"• المستخدم ← {target.mention}\n"
            f"• تم ترقيته إلى ← **{target_role_name}**"
        )

    elif action == "تنزيل":
        remove_role(chat.id, target.id)
        await message.reply_text(
            f"• المستخدم ← {target.mention}\n"
            f"• تم تنزيله إلى ← **عضو**"
        )