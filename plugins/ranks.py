from pyrogram import Client, filters
from database import get_role, set_role, remove_role
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import ChatPrivileges

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


# 🔹 توحيد جلب الرتبة (الافتراضي عضو)
def get_user_role(chat_id, user_id):
    role = get_role(chat_id, user_id)
    return 9 if role is None else role


admin_sessions = {}


# أمر يعرض رتبتك
@Client.on_message(filters.group & filters.regex("^رتبتي$"))
async def my_rank(client, message):
    sender = message.from_user
    chat = message.chat

    role_level = get_user_role(chat.id, sender.id)
    role_name = Roles.get(role_level, "عضو")

    await message.reply_text(f"• رتبتك هي ← **{role_name}**")


# أمر يعرض رتبة الشخص الذي رديت عليه
@Client.on_message(filters.group & filters.regex("^رتبته$"))
async def rtbth(client, message):
    chat = message.chat

    # التحقق من الرد على رسالة
    if not message.reply_to_message:
        return await message.reply_text("⚠️ لازم ترد على رسالة المستخدم لتعرف رتبته.")

    target = message.reply_to_message.from_user
    role_level = get_user_role(chat.id, target.id)
    role_name = Roles.get(role_level, "عضو")

    await message.reply_text(f"• رتبة المستخدم ← **{role_name}**")


role_pattern = "|".join(map(lambda x: x.replace(" ", r"\s"), ROLE_COMMANDS.keys()))


@Client.on_message(
    filters.group &
    filters.regex(rf"^(رفع|تنزيل)\s+({role_pattern})(?:\s+(.+))?$")
)
async def handle_roles(client, message):
    sender = message.from_user
    chat = message.chat
    text = message.text.strip()

    sender_role = get_user_role(chat.id, sender.id)

    # 🔒 فقط ادمن (7) وأعلى
    if sender_role > 7:
        # await message.reply_text("⚠️ يجب أن تكون ادمن على الأقل.")
        return

    parts = text.split()

    if len(parts) < 2:
        return

    action = parts[0]
    target_role_name = parts[1]
    target_role_level = ROLE_COMMANDS.get(target_role_name)

    # 🔒 تحقق من صحة الرتبة
    if target_role_level is None:
        await message.reply_text("⚠️ رتبة غير معروفة.")
        return

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

    # 🔒 منع تعديل النفس
    if target.id == sender.id:
        await message.reply_text("⚠️ لا يمكنك تعديل رتبتك بنفسك.")
        return

    target_current_role = get_user_role(chat.id, target.id)

    # 🔒 حماية المطور الأساسي
    if target_current_role == 0:
        await message.reply_text("⛔ لا يمكن تعديل رتبة المطور الأساسي.")
        return

    # 🔒 لا يمكن تعديل شخص أعلى أو مساوي لك
    if target_current_role <= sender_role:
        await message.reply_text("⚠️ لا يمكنك تعديل شخص أعلى منك أو مساوي لك.")
        return

    # 🔒 لا يمكن منحه رتبة أعلى منك أو مساوية لك
    if target_role_level <= sender_role:
        await message.reply_text("⚠️ لا يمكنك منحه رتبة أعلى منك أو مساوية لك.")
        return

    # 🔹 تنفيذ العملية
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


@Client.on_message(filters.group & filters.regex(r"^تنزيل الكل(?:\s+(.+))?$"))
async def demote_all(client, message):
    sender = message.from_user
    chat = message.chat
    sender_role = get_user_role(chat.id, sender.id)

    # 🔒 فقط ادمن (7) وأعلى
    if sender_role > 7:
        await message.reply_text("⚠️ يجب أن تكون ادمن على الأقل.")
        return

    target = None

    # الحالة 1: بالرد
    if message.reply_to_message:
        target = message.reply_to_message.from_user

    # الحالة 2: باليوزر
    elif message.matches and message.matches[0].group(1):
        username = message.matches[0].group(1).replace("@", "")
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

    # 🔒 منع تنزيل النفس
    if target.id == sender.id:
        await message.reply_text("⚠️ لا يمكنك تنزيل نفسك.")
        return

    target_role = get_user_role(chat.id, target.id)

    # 🔒 حماية المطور الأساسي
    if target_role == 0:
        await message.reply_text("⛔ لا يمكن تنزيل المطور الأساسي.")
        return

    # 🔒 لا يمكن تنزيل شخص أعلى أو مساوي لك
    if target_role <= sender_role:
        await message.reply_text("⚠️ لا يمكنك تنزيل شخص أعلى منك أو مساوي لك.")
        return

    # تنفيذ التنزيل
    remove_role(chat.id, target.id)

    await message.reply_text(
        f"• المستخدم ← {target.mention}\n"
        f"• تم تنزيله من جميع الرتب وأصبح **عضو**"
    )


# رفع مشرف
@Client.on_message(filters.group & filters.regex(r"^رفع مشرف(?:\s+(.+))?$"))
async def promote_menu(client, message):
    chat_id = message.chat.id
    admin_id = message.from_user.id
    sender_role = get_user_role(chat_id, admin_id)

    if sender_role > 4:  # تحقق من الصلاحية
        return await message.reply_text("⚠️ يجب أن تكون ادمن على الأقل.")

    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif message.matches and message.matches[0].group(1):
        try:
            target = await client.get_users(message.matches[0].group(1).replace("@", ""))
        except Exception:
            return await message.reply_text("⚠️ لم يتم العثور على المستخدم.")
    else:
        return await message.reply_text("⚠️ لازم ترد على شخص أو تكتب يوزره.")

    # if target.id == admin_id:
    #     return await message.reply_text("⚠️ لا يمكنك رفع نفسك.")

    # إرسال زر تعديل الصلاحيات فقط
    await message.reply_text(
        f"• صلاحيات المستخدم -",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("تعديل الصلاحيات", callback_data=f"openperm:{target.id}")]]
        )
    )


# فتح كيبورد الصلاحيات
@Client.on_callback_query(filters.regex("^openperm:"))
async def open_permissions(client, callback):
    user_id = int(callback.data.split(":")[1])
    chat_id = callback.message.chat.id
    await callback.message.edit_reply_markup(
        await build_keyboard_runtime(client, chat_id, user_id)
    )


# التعامل مع أزرار الصلاحيات
@Client.on_callback_query(filters.regex("^perm:"))
async def handle_perm_buttons(client, callback):
    _, action, user_id = callback.data.split(":")
    user_id = int(user_id)
    chat_id = callback.message.chat.id
    admin_id = callback.from_user.id

    # تحقق من صلاحية الشخص الذي يضغط الزر
    sender_role = get_user_role(chat_id, admin_id)
    if sender_role > 4:  # تحقق من الصلاحية
        return await callback.answer("⚠️ لا تملك صلاحية.", show_alert=True)

    member = await client.get_chat_member(chat_id, user_id)

    # إذا لم يكن للمستخدم أي صلاحيات، أعطه صلاحيات أساسية أولية
    if not member.privileges:
        await client.promote_chat_member(
            chat_id, user_id,
            privileges=ChatPrivileges(can_manage_chat=False, can_manage_video_chats=True)
        )
        member = await client.get_chat_member(chat_id, user_id)

    perms = member.privileges or ChatPrivileges()

    if action == "close":
        return await callback.message.delete()

    changes = {}
    if action == "can_change_info":
        changes["can_change_info"] = not perms.can_change_info
        message_text = "• تم صلاحيه تغيير المعلومات" if not perms.can_promote_members else "• تم تعطيل صلاحيه تغيير المعلومات"
    elif action == "can_pin_messages":
        changes["can_pin_messages"] = not perms.can_pin_messages
        message_text = "• تم تفعيل صلاحيه التثبيت" if not perms.can_promote_members else "• تم تعطيل صلاحيه التثبيت"
    elif action == "can_restrict_members":
        changes["can_restrict_members"] = not perms.can_restrict_members
        message_text = "• تم تفعيل صلاحيه الحظر" if not perms.can_promote_members else "• تم تعطيل صلاحيه صلاحيه الحظر"
    elif action == "can_invite_users":
        changes["can_invite_users"] = not perms.can_invite_users
        message_text = "• تم تفعيل صلاحيه دعوه المستخدمين" if not perms.can_promote_members else "• تم تعطيل صلاحيه دعوه المستخدمين"
    elif action == "can_delete_messages":
        changes["can_delete_messages"] = not perms.can_delete_messages
        message_text = "• تم تفعيل صلاحيه مسح الرسائل" if not perms.can_promote_members else "• تم تعطيل صلاحيه مسح الرسائل"
    elif action == "can_promote_members":
        changes["can_promote_members"] = not perms.can_promote_members
        message_text = "• تم تفعيل صلاحيه اضافه مشرفين" if not perms.can_promote_members else "• تم تعطيل صلاحيه اضافه مشرفين"

    # قلب الصلاحية المطلوبة
    kwargs = {
        "can_change_info": perms.can_change_info if action != "can_change_info" else not perms.can_change_info,
        "can_pin_messages": perms.can_pin_messages if action != "can_pin_messages" else not perms.can_pin_messages,
        "can_restrict_members": perms.can_restrict_members if action != "can_restrict_members" else not perms.can_restrict_members,
        "can_invite_users": perms.can_invite_users if action != "can_invite_users" else not perms.can_invite_users,
        "can_delete_messages": perms.can_delete_messages if action != "can_delete_messages" else not perms.can_delete_messages,
        "can_promote_members": perms.can_promote_members if action != "can_promote_members" else not perms.can_promote_members,
        "can_manage_video_chats": perms.can_manage_video_chats
    }

    await client.promote_chat_member(chat_id, user_id, privileges=ChatPrivileges(**kwargs))

    # تحديث الكيبورد مع تجنب MESSAGE_NOT_MODIFIED
    new_markup = await build_keyboard_runtime(client, chat_id, user_id)
    try:
        if callback.message.reply_markup != new_markup:
            await callback.message.edit_reply_markup(new_markup)
    except pyrogram.errors.MessageNotModified:
        pass

    await callback.answer(message_text, show_alert=True)


# بناء كيبورد الصلاحيات
async def build_keyboard_runtime(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    perms = member.privileges or ChatPrivileges()

    def mark(x): return "❬ ✔️ ❭" if x else "❬ ❌ ❭"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"- تغيير معلومات الجروب : {mark(perms.can_change_info)}",
                              callback_data=f"perm:can_change_info:{user_id}")],
        [InlineKeyboardButton(f"- تثبيت الرسائل : {mark(perms.can_pin_messages)}",
                              callback_data=f"perm:can_pin_messages:{user_id}")],
        [InlineKeyboardButton(f"- حظر المستخدمين : {mark(perms.can_restrict_members)}",
                              callback_data=f"perm:can_restrict_members:{user_id}")],
        [InlineKeyboardButton(f"- دعوة المستخدمين : {mark(perms.can_invite_users)}",
                              callback_data=f"perm:can_invite_users:{user_id}")],
        [InlineKeyboardButton(f"- مسح الرسائل : {mark(perms.can_delete_messages)}",
                              callback_data=f"perm:can_delete_messages:{user_id}")],
        [InlineKeyboardButton(f"- اضافة مشرفين : {mark(perms.can_promote_members)}",
                              callback_data=f"perm:can_promote_members:{user_id}")],
        [InlineKeyboardButton("- اخفاء الامر", callback_data=f"perm:close:{user_id}")]
    ])


@Client.on_message(filters.group & filters.regex(r"^صلاحياتي$"))
async def GetMyPrem(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # جلب معلومات العضو
    member = await client.get_chat_member(chat_id, user_id)
    perms = member.privileges or ChatPrivileges()

    # دالة لتحديد علامة ✔️ أو ❌
    def mark(x):
        return "❬ ✔️ ❭" if x else "❬ ❌ ❭"

    # تحديد رتبة المستخدم (عضو، مشرف، ادمن)
    if member.status == "creator":
        role = "مالك الجروب"
    elif member.privileges:
        role = "مشرف الجروب"
    else:
        role = "عضو"

    text = f"""• الصلاحيات : {role}
    • صلاحيات المستخدم :
    ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉ ┉
    • تغيير المعلومات : {mark(perms.can_change_info)}
    • تثبيت الرسائل : {mark(perms.can_pin_messages)}
    • اضافه مستخدمين : {mark(perms.can_invite_users)}
    • مسح الرسائل : {mark(perms.can_delete_messages)}
    • حظر المستخدمين : {mark(perms.can_restrict_members)}
    • اضافه المشرفين : {mark(perms.can_promote_members)}"""

    await message.reply_text(text)


@Client.on_message(filters.group & filters.regex(r"^تنزيل مشرف(?:\s+(.+))?$"))
async def demote_admin(client, message):
    chat_id = message.chat.id
    admin_id = message.from_user.id
    sender_role = get_user_role(chat_id, admin_id)

    # تحقق من صلاحية الشخص الذي ينفذ الأمر
    if sender_role > 4:  # يجب أن يكون ادمن على الأقل
        return await message.reply_text("⚠️ يجب أن تكون ادمن على الأقل لتنزيل مشرف.")

    # تحديد الهدف
    target = None
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif message.matches and message.matches[0].group(1):
        try:
            target = await client.get_users(message.matches[0].group(1).replace("@", ""))
        except Exception:
            return await message.reply_text("⚠️ لم يتم العثور على المستخدم.")
    else:
        return await message.reply_text("⚠️ لازم ترد على شخص أو تكتب يوزره.")

    # # منع تنزيل نفسك
    # if target.id == admin_id:
    #     return await message.reply_text("⚠️ لا يمكنك تنزيل نفسك.")

    # تنزيل كل الصلاحيات
    await client.promote_chat_member(
        chat_id,
        target.id,
        privileges=ChatPrivileges(
            can_change_info=False,
            can_invite_users=False,
            can_delete_messages=False,
            can_promote_members=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_manage_video_chats=False,
            can_edit_messages=False,
            can_post_messages=False,
            can_manage_chat=False,
        ),
    )

    await message.reply_text(
        f"""
        • المستخدم ← {target.mention}
• تم تنزيله من المشرفين
        
        """
    )
