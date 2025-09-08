import os
import logging
import random
from flask import Flask, request
import telebot
from telebot import types

# --------- ENV ----------
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL", "")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable topilmadi!")
if not APP_URL:
    raise ValueError("APP_URL environment variable topilmadi!")
APP_URL = APP_URL.rstrip("/")  # trailing slash bo'lsa olib tashlaymiz

# --------- BOT / FLASK ----------
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")
server = Flask(__name__)

# --------- LOGGING ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------- ADMIN / KANAL ----------
ADMIN_ID = 7850048970                  # sening admin ID'ing
CHANNEL_ID = -1003045379122            # yopiq kanal ID'ing

# --------- USER STORAGE (oddiy RAM) ----------
# RAMda saqlanadi (deploy/restart bo'lsa tozalanadi)
# chat_id -> {"id": "<user_linebet_id_yozgan>", "confirmed": bool}
users = {}

# --------- MENYU ----------
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    kb.row("📸 Skrinshot yuborish", "🔔 Signal olish")
    kb.row("📊 Statistika")
    return kb

# --------- /start ----------
@bot.message_handler(commands=["start"])
def cmd_start(message: types.Message):
    users.setdefault(message.chat.id, {"id": None, "confirmed": False})
    txt = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Quyidagi tugmalardan foydalaning 👇\n\n"
        "❗️ *Diqqat!* Bot faqat **LINEBET** uchun ishlaydi.\n"
        "👉 Ro'yxatdan o'tishda *PROMOKOD* joyiga albatta **FOYDA50** yozing.\n"
        "📸 Ro'yxatdan o'tganingizni tasdiqlash uchun *Skrinshot yuboring*."
    )
    bot.send_message(message.chat.id, txt, reply_markup=main_menu())

# --------- TEXTLAR ----------
@bot.message_handler(func=lambda m: True, content_types=["text"])
def on_text(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    users.setdefault(chat_id, {"id": None, "confirmed": False})

    if text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            chat_id,
            "📝 Ro'yxatdan o'tish uchun havolalar:\n\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n"
            "👉 https://uzb.bonus-linebet.com/foyda50\n\n"
            "ℹ️ *O‘zingizga qulay bo‘lganidan ro‘yxatdan o‘ting.*\n"
            "⚠️ *FOYDA50* promokodini *to‘liq* kiriting — bu **LINEBET** uchun *majburiy*."
        )

    elif text == "▶️ Davom etish":
        msg = bot.send_message(chat_id, "🔑 *ID raqamingizni* kiriting:")
        bot.register_next_step_handler(msg, save_user_id)

    elif text == "📸 Skrinshot yuborish":
        bot.send_message(
            chat_id,
            "📸 Iltimos, ro‘yxatdan o‘tganingizni tasdiqlovchi *skrinshotni* yuboring.\n\n"
            "⚠️ *Eslatma:* faqat **FOYDA50** promokodi bilan ro‘yxatdan o‘tilgan hisoblar tasdiqlanadi (LINEBET)."
        )

    elif text == "🔔 Signal olish":
        info = users.get(chat_id, {})
        if not info.get("confirmed"):
            bot.send_message(
                chat_id,
                "⛔ Siz hali *tasdiqlanmagansiz!*\n"
                "📸 Avval skrinshot yuboring va *admin tasdiqlashini* kuting."
            )
            return
        n = random.randint(1, 5)
        bot.send_message(
            chat_id,
            f"📡 Signal: *{n}* 🍎\n\n"
            "⚠️ Eslatma!\n"
            "👉 Bot faqat **LINEBET** uchun ishlaydi.\n"
            "👉 Promokod joyiga albatta *FOYDA50* yozing.\n"
            "❌ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!"
        )

    elif text == "📊 Statistika":
        if chat_id != ADMIN_ID:
            bot.send_message(chat_id, "❌ Bu bo‘lim faqat *admin* uchun!")
            return
        total = len(users)
        confirmed = sum(1 for u in users.values() if u.get("confirmed"))
        with_id = sum(1 for u in users.values() if u.get("id"))
        bot.send_message(
            chat_id,
            f"📊 Statistika\n"
            f"👥 Jami foydalanuvchilar: *{total}*\n"
            f"🆔 ID kiritganlar: *{with_id}*\n"
            f"✅ Tasdiqlanganlar: *{confirmed}*"
        )

# --------- ID saqlash ----------
def save_user_id(message: types.Message):
    chat_id = message.chat.id
    users.setdefault(chat_id, {"id": None, "confirmed": False})
    users[chat_id]["id"] = message.text.strip()
    bot.send_message(
        chat_id,
        f"✅ ID qabul qilindi: *{users[chat_id]['id']}*\n"
        "📸 Endi ro‘yxatdan o‘tganingizni tasdiqlovchi *skrinshotni yuboring*."
    )

# --------- SKRINSHOT QABUL ----------
@bot.message_handler(content_types=["photo"])
def on_photo(message: types.Message):
    chat_id = message.chat.id
    users.setdefault(chat_id, {"id": None, "confirmed": False})

    file_id = message.photo[-1].file_id  # eng katta rasm sifatini olamiz

    # Kanalga yuboriladigan xabar + inline tugmalar (faqat admin bosishi kerak)
    caption = (
        f"📥 *Yangi skrinshot*\n"
        f"👤 UserID: `{chat_id}`\n"
        f"🆔 Linebet ID: `{users[chat_id]['id']}`\n"
        f"— — —\n"
        f"Quyidagi tugmalar orqali tasdiqlang yoki rad eting."
    )
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{chat_id}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{chat_id}")
    )

    try:
        bot.send_photo(CHANNEL_ID, file_id, caption=caption, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        logger.exception("Kanalga yuborishda xatolik:")
        bot.send_message(
            chat_id,
            "⚠️ Xatolik: rasm kanalga yuborilmadi.\n"
            "Iltimos, bot *kanalga admin* qilinganini tekshiring (Post Messages ruxsati)."
        )
        return

    # Foydalanuvchiga eslatma
    bot.send_message(
        chat_id,
        "📩 *Skrinshot qabul qilindi!*\n"
        "✅ Endi *admin tasdiqlashini* kuting.\n\n"
        "⚠️ *Eslatma:* faqat **FOYDA50** promokodi bilan ro‘yxatdan o‘tilgan hisoblar tasdiqlanadi (LINEBET)."
    )

# --------- ADMIN CALLBACK (tasdiqlash / rad etish) ----------
@bot.callback_query_handler(func=lambda c: c.data.startswith(("approve_", "reject_")))
def on_callback(c: types.CallbackQuery):
    # faqat ADMIN tugma bossin
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "⛔ Faqat admin tasdiqlay oladi.")
        return

    action, user_str = c.data.split("_", 1)
    target_id = int(user_str)

    users.setdefault(target_id, {"id": None, "confirmed": False})

    if action == "approve":
        users[target_id]["confirmed"] = True
        # foydalanuvchiga xabar
        bot.send_message(
            target_id,
            "✅ *Skrinshotingiz tasdiqlandi!*\n"
            "Endi *🔔 Signal olish* tugmasidan foydalanishingiz mumkin."
        )
        # kanaldagi caption'ni yangilash (tasdiqlandi deb)
        try:
            new_caption = (c.message.caption or "") + "\n\n✅ *Tasdiqlandi*"
            bot.edit_message_caption(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                caption=new_caption,
                parse_mode="Markdown",
                reply_markup=None
            )
        except Exception:
            pass
        bot.answer_callback_query(c.id, "Tasdiqlandi ✅")

    elif action == "reject":
        users[target_id]["confirmed"] = False
        # foydalanuvchiga xabar
        bot.send_message(
            target_id,
            "❌ *Skrinshotingiz tasdiqlanmadi.*\n"
            "Iltimos, **FOYDA50** promokodi bilan ro‘yxatdan o‘tib *to‘g‘ri skrinshot* yuboring va qayta urinib ko‘ring."
        )
        # kanaldagi caption'ni yangilash (rad etildi)
        try:
            new_caption = (c.message.caption or "") + "\n\n❌ *Rad etildi*"
            bot.edit_message_caption(
                chat_id=c.message.chat.id,
                message_id=c.message.message_id,
                caption=new_caption,
                parse_mode="Markdown",
                reply_markup=None
            )
        except Exception:
            pass
        bot.answer_callback_query(c.id, "Rad etildi ❌")

# --------- WEBHOOK ROUTES ----------
@server.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@server.route("/", methods=["GET"])
def index():
    # har chaqirilganda webhook adresini qayta qo'yamiz (APP_URL mustahkam)
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    return "Webhook OK", 200

if __name__ == "__main__":
    # Lokal ishga tushirish uchun
    port = int(os.environ.get("PORT", 8080))
    server.run(host="0.0.0.0", port=port)


