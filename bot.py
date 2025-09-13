import os
import logging
import random
from flask import Flask, request
import telebot
from telebot import types

# --------- ENV ----------
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL", "").rstrip("/")
if not TOKEN or not APP_URL:
    raise ValueError("BOT_TOKEN yoki APP_URL environment variable topilmadi!")

# --------- BOT / WEBHOOK ----------
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
server = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------- ADMIN & KANALLAR ----------
ADMIN_ID = 7850048970
CHANNEL_ID = -1003045379122      # adminga skrinshot tushadigan kanal
SUB_CHANNEL_ID = -1002753581203  # majburiy obuna bo‘ladigan kanal
SUB_CHANNEL_LINK = "https://t.me/+W8CTOv6AhYhhYzRi"  # invite link

# --------- USERLAR SAQLOVCHI ----------
users = {}

# --------- OBUNA TEKSHIRUV FUNKSIYASI ----------
def check_subscription(user_id):
    try:
        status = bot.get_chat_member(SUB_CHANNEL_ID, user_id).status
        return status in ("member", "administrator", "creator")
    except Exception as e:
        logger.warning(f"Obuna tekshiruvida muammo: {e}")
        return False

# --------- ASOSIY MENYU ----------
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    kb.row("📸 Skrinshot yuborish", "🔔 Signal olish")
    kb.row("📊 Statistika", "/start")
    return kb

# --------- /start HANDLER ----------
@bot.message_handler(commands=["start"])
def cmd_start(message: types.Message):
    users.setdefault(message.chat.id, {"id": None, "confirmed": False})
    txt = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Eslatma! Bot to‘g‘ri ishlashi uchun:\n"
        "1) 🟢 Vzlom ilovalarni yuklab oling (pastdagi 📥 Yuklab olish tugmasidan foydalaning)\n"
        "2) Ro‘yxatdan o‘tishda *PROMOKOD* joyiga albatta **FOYDA50** yozing\n"
        "3) Hisobingizni kattaroq summaga to‘ldiring (masalan *200.000 so‘m*)\n"
        "4) Botga o‘sha ro‘yxatdan o‘tgan *profil ID* sini yuboring\n"
        "5) ⚠️ Agar noto‘g‘ri yoki feyk ID yuborilsa — bot *xato signal* ko‘rsatadi!"
    )
    bot.send_message(message.chat.id, txt, reply_markup=main_menu())

# --------- MATN HANDLING ----------
@bot.message_handler(func=lambda m: True, content_types=["text"])
def on_text(message: types.Message):
    user = message.chat.id
    text = message.text.strip()

    # Obuna shart
    if not check_subscription(user):
        bot.send_message(
            user,
            f"⛔ Botdan foydalanish uchun avval kanalga qo‘shiling:\n👉 {SUB_CHANNEL_LINK}"
        )
        return

    if text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            user,
            "📝 Ro'yxatdan o'tish uchun havolalar:\n\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n"
            "👉 https://uzb.bonus-linebet.com/foyda50\n\n"
            "ℹ️ O‘zingizga qulay bo‘lganidan ro‘yxatdan o‘ting.\n"
            "⚠️ Promokod joyiga albatta *FOYDA50* yozing!"
        )

    elif text == "▶️ Davom etish":
        msg = bot.send_message(user, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, save_user_id)

    elif text == "📸 Skrinshot yuborish":
        bot.send_message(user, "📸 Skrinshot yuboring, tasdiqlash uchun adminga yuboramiz.")

    elif text == "🔔 Signal olish":
        u = users.get(user, {})
        if not u.get("confirmed"):
            bot.send_message(user, "❌ Siz hali tasdiqlanmadingiz. 📸 Skrinshot yuboring.")
        else:
            signal = random.randint(1, 5)
            txt = (
                f"📡 Signal: *{signal}* 🍎\n\n"
                "❗️ Eslatma!\n"
                "👉 Bot faqat **LINEBET** uchun ishlaydi.\n"
                "👉 Promokod joyiga albatta *FOYDA50* yozing.\n"
                "❌ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!"
            )
            bot.send_message(user, txt)

    elif text == "📊 Statistika":
        if user == ADMIN_ID:
            total = len(users)
            confirmed = sum(1 for u in users.values() if u["confirmed"])
            bot.send_message(user, f"📊 Foydalanuvchilar: {total}, Tasdiqlanganlar: {confirmed}")
        else:
            bot.send_message(user, "❌ Bu bo‘lim faqat admin uchun!")

    elif text.startswith("/send "):
        if user == ADMIN_ID:
            txt = text.split(" ", 1)[1]
            count = 0
            for uid in users:
                if check_subscription(uid):
                    try:
                        bot.send_message(uid, txt)
                        count += 1
                    except:
                        pass
            bot.send_message(user, f"📩 Xabar {count} foydalanuvchiga yuborildi.")
        else:
            bot.send_message(user, "⛔ Sizda ruxsat yo‘q.")

# --------- SKRINSHOT QABUL QILISH ----------
@bot.message_handler(content_types=["photo"])
def on_photo(message: types.Message):
    user = message.chat.id
    users.setdefault(user, {"id": None, "confirmed": False})

    # Rasmni olish
    file_id = message.photo[-1].file_id

    # Adminga yuborish
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{user}"),
        types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"reject_{user}")
    )
    bot.send_photo(
        CHANNEL_ID,
        file_id,
        caption=f"📸 Yangi skrinshot!\n👤 User: `{user}`",
        reply_markup=kb
    )
    bot.send_message(user, "📤 Skrinshot adminga yuborildi, kuting...")

# --------- ADMIN CALLBACK ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith(("confirm_", "reject_")))
def on_callback(call: types.CallbackQuery):
    action, uid = call.data.split("_")
    uid = int(uid)

    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Siz admin emassiz!")
        return

    if action == "confirm":
        users.setdefault(uid, {"id": None, "confirmed": False})
        users[uid]["confirmed"] = True
        bot.send_message(uid, "✅ Skrinshotingiz tasdiqlandi! Endi botdan to‘liq foydalanishingiz mumkin.")
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption="✅ Tasdiqlandi!"
        )
    else:
        users.setdefault(uid, {"id": None, "confirmed": False})
        users[uid]["confirmed"] = False
        bot.send_message(uid, "❌ Skrinshot rad etildi.")
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption="❌ Rad etildi!"
        )

# --------- ID saqlash ----------
def save_user_id(message: types.Message):
    user = message.chat.id
    users.setdefault(user, {"id": None, "confirmed": False})
    users[user]["id"] = message.text.strip()
    bot.send_message(user, f"✅ ID qabul qilindi: {users[user]['id']}")

# --------- WEBHOOK ROUTES ----------
@server.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@server.route("/", methods=["GET"])
def index():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    return "Webhook ok", 200

if __name__ == "__main__":import os
import logging
import random
import json
from flask import Flask, request
import telebot
from telebot import types

# --------- ENV ----------
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL", "").rstrip("/")
if not TOKEN or not APP_URL:
    raise ValueError("BOT_TOKEN yoki APP_URL environment variable topilmadi!")

# --------- BOT / WEBHOOK ----------
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
server = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------- ADMIN & KANALLAR ----------
ADMIN_ID = 7850048970
CHANNEL_ID = -1003045379122      # Admin qaror chiqaradigan (mahfiy) kanal
SUB_CHANNEL_ID = -1002753581203  # Majburiy obuna kanali
SUB_CHANNEL_LINK = "https://t.me/+W8CTOv6AhYhhYzRi"

# --------- USERLAR SAQLASH ----------
USERS_FILE = "users.json"
users = {}

def load_users():
    global users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
            users = {int(k): v for k, v in users.items()}  # kalitlarni int qilish
        except:
            users = {}
    else:
        users = {}

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# Ishga tushganda mavjud foydalanuvchilarni yuklash
load_users()

# --------- OBUNA TEKSHIRUV FUNKSIYASI ----------
def check_subscription(user_id):
    try:
        status = bot.get_chat_member(SUB_CHANNEL_ID, user_id).status
        return status in ("member", "administrator", "creator")
    except Exception as e:
        logger.warning(f"Obuna tekshiruvida muammo: {e}")
        return False

# --------- ASOSIY MENYU ----------
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    kb.row("🔔 Signal olish", "📊 Statistika")
    kb.row("/start")
    return kb

# --------- /start HANDLER ----------
@bot.message_handler(commands=["start"])
def cmd_start(message: types.Message):
    users.setdefault(message.chat.id, {"id": None, "confirmed": False})
    save_users()  # saqlash

    txt = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Eslatma! Bot to‘g‘ri ishlashi uchun:\n"
        "1) 🟢 Ilovani yuklab oling\n"
        "2) Ro‘yxatdan o‘tishda *PROMOKOD* joyiga **FOYDA50** yozing\n"
        "3) Hisobingizni *200.000 so‘m* va undan ko‘proqqa to‘ldiring\n"
        "4) Botga ro‘yxatdan o‘tgan *profil ID* sini yuboring\n"
        "5) ✅ Tasdiqlash uchun adminga yozing: @jasuroo77"
    )
    bot.send_message(message.chat.id, txt, reply_markup=main_menu())

    # Admin kanaliga xabar yuborish
    username = f"@{message.from_user.username}" if message.from_user.username else "❌ Username yo‘q"
    fullname = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Ruxsat berish", callback_data=f"confirm_{message.chat.id}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{message.chat.id}")
    )
    bot.send_message(
        CHANNEL_ID,
        f"👤 Yangi foydalanuvchi\n"
        f"🆔 ID: `{message.chat.id}`\n"
        f"🔗 Username: {username}\n"
        f"📛 Full name: {fullname}",
        reply_markup=kb
    )

# --------- MATN HANDLING ----------
@bot.message_handler(func=lambda m: True, content_types=["text"])
def on_text(message: types.Message):
    user = message.chat.id
    text = message.text.strip()

    # Obuna shart
    if not check_subscription(user):
        bot.send_message(
            user,
            f"⛔ Botdan foydalanish uchun avval kanalga qo‘shiling:\n👉 {SUB_CHANNEL_LINK}"
        )
        return

    if text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            user,
            "📝 Ro'yxatdan o'tish havolalari:\n\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n"
            "👉 https://uzb.bonus-linebet.com/foyda50\n\n"
            "⚠️ Promokod joyiga *FOYDA50* yozishni unutmang!"
        )

    elif text == "▶️ Davom etish":
        msg = bot.send_message(user, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, save_user_id)

    elif text == "🔔 Signal olish":
        u = users.get(user, {})
        if not u.get("confirmed"):
            bot.send_message(user, "❌ Siz hali tasdiqlanmadingiz. Adminga yozing: @jasuroo77")
        else:
            signal = random.randint(1, 5)
            txt = (
                f"📡 Signal: *{signal}* 🍎\n\n"
                "❗️ Eslatma!\n"
                "👉 Bot faqat **LINEBET** uchun ishlaydi.\n"
                "👉 Promokod joyiga *FOYDA50* yozing."
            )
            bot.send_message(user, txt)

    elif text == "📊 Statistika":
        if user == ADMIN_ID:
            total = len(users)
            confirmed = sum(1 for u in users.values() if u["confirmed"])
            bot.send_message(user, f"📊 Foydalanuvchilar: {total}, Tasdiqlangan: {confirmed}")
        else:
            bot.send_message(user, "❌ Bu bo‘lim faqat admin uchun!")

    elif text.startswith("/send "):
        if user == ADMIN_ID:
            txt = text.split(" ", 1)[1]
            count = 0
            for uid in users:
                try:
                    bot.send_message(uid, txt)
                    count += 1
                except:
                    pass
            bot.send_message(user, f"📩 Xabar {count} foydalanuvchiga yuborildi.")
        else:
            bot.send_message(user, "⛔ Sizda ruxsat yo‘q.")

# --------- ADMIN CALLBACK (kanal orqali tasdiqlash) ----------
@bot.callback_query_handler(func=lambda call: call.data.startswith(("confirm_", "reject_")))
def on_callback(call: types.CallbackQuery):
    action, uid = call.data.split("_")
    uid = int(uid)

    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "⛔ Siz admin emassiz!")
        return

    if action == "confirm":
        users.setdefault(uid, {"id": None, "confirmed": False})
        users[uid]["confirmed"] = True
        save_users()
        bot.send_message(uid, "✅ Admin sizga ruxsat berdi. Endi botdan foydalanishingiz mumkin.")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✅ Ruxsat berildi!"
        )
    else:
        users.setdefault(uid, {"id": None, "confirmed": False})
        users[uid]["confirmed"] = False
        save_users()
        bot.send_message(uid, "❌ Admin sizga ruxsat bermadi.")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ Ruxsat rad etildi!"
        )

# --------- ID saqlash ----------
def save_user_id(message: types.Message):
    user = message.chat.id
    users.setdefault(user, {"id": None, "confirmed": False})
    users[user]["id"] = message.text.strip()
    save_users()
    bot.send_message(user, f"✅ ID qabul qilindi: {users[user]['id']}")

# --------- WEBHOOK ROUTES ----------
@server.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@server.route("/", methods=["GET"])
def index():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    return "Webhook ok", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))



