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

# --------- ADMIN / KANALLAR ----------
ADMIN_ID = 7850048970                 # sizning admin ID
CHANNEL_ID = -1003045379122           # skrinshotlar yuboriladigan kanal
SUB_CHANNEL_ID = -1002753581203       # majburiy obuna kanali (yopiq)

# --------- USER STORAGE ----------
users = {}  # {chat_id: {"id": "...", "confirmed": True/False}}

# --------- MENYU ----------
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    kb.row("📸 Skrinshot yuborish", "🔔 Signal olish")
    kb.row("📊 Statistika")
    return kb

# --------- OBUNA TEKSHIRISH ----------
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(SUB_CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.warning(f"Obuna tekshirishda xatolik: {e}")
        return False

# --------- /start ----------
@bot.message_handler(commands=["start"])
def cmd_start(message: types.Message):
    users.setdefault(message.chat.id, {"id": None, "confirmed": False})
    txt = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Quyidagi tugmalardan foydalaning 👇\n\n"
        "❗️ *Diqqat!* Bot faqat **LINEBET** uchun ishlaydi.\n"
        "👉 Ro'yxatdan o'tishda *PROMOKOD* joyiga albatta **FOYDA50** yozing.\n"
        "💰 Hisobingizni kamida *50 000 yoki 100 000 so‘mga* to‘ldiring.\n"
        "📸 Ro'yxatdan o'tganingizni tasdiqlash uchun *Skrinshot yuboring*.\n\n"
        f"📥 Avval [Kanalga obuna bo‘ling](https://t.me/+W8CTOv6AhYhhYzRi)!"
    )
    bot.send_message(message.chat.id, txt, reply_markup=main_menu(), disable_web_page_preview=True)

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
            "👉 https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n\n"
            "⚠️ PROMOKOD joyiga *FOYDA50* yozing."
        )

    elif text == "▶️ Davom etish":
        msg = bot.send_message(chat_id, "🔑 *ID raqamingizni* kiriting:")
        bot.register_next_step_handler(msg, save_user_id)

    elif text == "📸 Skrinshot yuborish":
        bot.sen

