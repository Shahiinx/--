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


