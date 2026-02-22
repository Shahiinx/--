import sqlite3
from config import OWNER_ID  # OWNER_ID ممكن يكون رقم أو قائمة أرقام
DB_NAME = "securitybot.db"

# =====================
# تهيئة قاعدة البيانات
# =====================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # جدول الرتب لكل جروب
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            chat_id INTEGER,
            user_id INTEGER,
            role_level INTEGER,
            PRIMARY KEY(chat_id, user_id)
        )
    """)

    # جدول حماية الجروبات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS protections (
            chat_id INTEGER PRIMARY KEY,
            links INTEGER DEFAULT 1,
            spam INTEGER DEFAULT 1,
            bots INTEGER DEFAULT 1,
            media INTEGER DEFAULT 1,
            forward INTEGER DEFAULT 1,
            mention INTEGER DEFAULT 1,
            edits INTEGER DEFAULT 1
        )
    """)


    cursor.execute("""
        INSERT OR IGNORE INTO roles (chat_id, user_id, role_level)
        VALUES (?, ?, ?)
    """, (0, OWNER_ID, 0))  # 0 = المطور الأساسي

    conn.commit()
    conn.close()


# =====================
# دوال الرتب
# =====================
def set_role(chat_id: int, user_id: int, role_level: int):
    """تعيين أو تحديث رتبة عضو"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO roles (chat_id, user_id, role_level)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id, user_id) DO UPDATE SET role_level=excluded.role_level
    """, (chat_id, user_id, role_level))
    conn.commit()
    conn.close()


def get_role(chat_id: int, user_id: int) -> int:
    """جلب رتبة عضو"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # أولاً: تحقق داخل الجروب
    cursor.execute("SELECT role_level FROM roles WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    result = cursor.fetchone()

    if result:
        conn.close()
        return result[0]

    # ثانياً: تحقق من الرتبة العامة (chat_id=0)
    cursor.execute("SELECT role_level FROM roles WHERE chat_id=0 AND user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 9  # 9 = العضو العادي


def remove_role(chat_id: int, user_id: int):
    """حذف رتبة عضو"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM roles WHERE chat_id=? AND user_id=?
    """, (chat_id, user_id))
    conn.commit()
    conn.close()


#  Groups Functions


def check_group(chat_id: int) -> str:
    """
    التحقق إذا الجروب موجود مسبقاً في قاعدة البيانات
    - إذا موجود: ترجع "تم التفعيل مسبقاً"
    - إذا جديد: تضيفه وتعيد "تم التفعيل"
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # تحقق إذا الجروب موجود في جدول الحماية
    cursor.execute("SELECT chat_id FROM protections WHERE chat_id=?", (chat_id,))
    result = cursor.fetchone()

    if result:
        conn.close()
        return "• تم تفعيلها مسبقا"

    # إذا الجروب جديد، أضفه ببيانات افتراضية
    cursor.execute("""
                   INSERT INTO protections (chat_id)
                   VALUES (?)
                   """, (chat_id,))
    conn.commit()
    conn.close()

    return "تم تفعيل البوت بنجاح"


def remove_premium(chat_id: int) -> int:
    """
    مسح جميع المميزين (role_level=8) داخل جروب محدد
    وتعيد عدد الأشخاص الذين تم مسحهم
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # أولاً نحسب عدد المميزين قبل الحذف
    cursor.execute("""
        SELECT COUNT(*) FROM roles
        WHERE chat_id=? AND role_level=8
    """, (chat_id,))
    result = cursor.fetchone()
    count = result[0] if result else 0

    # بعدين نمسحهم
    cursor.execute("""
        DELETE FROM roles
        WHERE chat_id=? AND role_level=8
    """, (chat_id,))

    conn.commit()
    conn.close()

    return count


# =====================
# دالة جلب أعضاء حسب الرتبة
# =====================
def get_members_by_role(chat_id: int, role_name: str) -> list:
    """
    ترجع قائمة user_id لكل الأعضاء في الجروب الذين يحملون رتبة معينة
    role_name: اسم الرتبة سواء المفرد أو الجمع مثل "مميز" أو "المميزين"
    """
    # جدول الرتب الأساسي
    Roles = {
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

    # قاموس الاسم الجمعي → الاسم الأساسي
    ROLE_PLURALS = {
        "الأعضاء": "عضو",
        "المميزين": "مميز",
        "الادمنية": "ادمن",
        "المدراء": "مدير",
        "المنشئين": "منشئ",
        "المنشئين الأساسيين": "منشئ أساسي",
        "المالكين": "مالك",
        "المالكين الأساسيين": "مالك أساسي",
        "المطورين": "مطور",
        "المطورين الأساسيين": "مطور أساسي"
    }

    # تحويل الاسم الجمعي إلى الاسم الأساسي إذا تم تمريره
    role_name = ROLE_PLURALS.get(role_name, role_name)

    role_level = Roles.get(role_name)
    if role_level is None:
        return []  # الرتبة غير موجودة

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id FROM roles WHERE chat_id=? AND role_level=?",
        (chat_id, role_level)
    )
    rows = cursor.fetchall()
    conn.close()

    return [user_id for (user_id,) in rows]