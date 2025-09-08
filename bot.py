import os
import telebot
import logging
from flask import Flask, request
import random

# === ENV VARIABLES ===
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable topilmadi!")

if not APP_URL:
    raise ValueError("APP_URL environment variable topilmadi!")

bot = telebot.TeleBot(TOKEN)

# === ADMIN ID (o‘zingizni Telegram ID qo‘ying) ===
ADMIN_ID = 123456789  # bu joyni o‘zingizga almashtiring
CHANNEL_ID = -1003045379122  # siz bergan yopiq kanal ID

# === Logging ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Foydalanuvchilar holati
user_status = {}

# === MENYU ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    markup.row("📸 Skrinshot yuborish")
    markup.row("🔔 Signal olish")
    return markup

# === START ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Botdan foydalanish uchun quyidagi bosqichlarni bajaring:\n\n"
        "1️⃣ Linebet orqali ro‘yxatdan o‘ting:\n"
        "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
        "👉 Linebet dasturi: https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n"
        "👉 Yangi havola: https://uzb.bonus-linebet.com/foyda50\n\n"
        "2️⃣ Hisobingizni kamida 💰 100 000 so‘mga to‘ldiring.\n"
        "3️⃣ Promokod: FOYDA50 ni to‘liq kiriting.\n\n"
        "⚠️ Agar skrinsiz yoki noto‘g‘ri promokod ishlatsangiz, signal bermaydi!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# === Matnlar ===
@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_message(message):
    if message.text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            message.chat.id,
            "📝 Ro'yxatdan o'tish uchun havolalar:\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 Linebet dasturi: https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n"
            "👉 Yangi havola: https://uzb.bonus-linebet.com/foyda50\n\n"
            "ℹ️ O‘zingizga qulay usuldan foydalanib ro‘yxatdan o‘ting."
        )

    elif message.text == "▶️ Davom etish":
        msg = bot.send_message(message.chat.id, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, get_id)

    elif message.text == "📸 Skrinshot yuborish":
        bot.send_message(
            message.chat.id,
            "📸 Linebet hisobingiz to‘ldirilgani va promokod FOYDA50 ishlatilganini ko‘rsatadigan skrinshot yuboring.\n\n"
            "✅ Admin tasdiqlamaguncha 'Signal olish' tugmasi ishlamaydi!"
        )
        user_status[message.chat.id] = "waiting_for_screenshot"

    elif message.text == "🔔 Signal olish":
        if user_status.get(message.chat.id) == "approved":
            random_number = random.randint(1, 5)
            bot.send_message(
                message.chat.id,
                f"🍎 Signal: {random_number}\n\n"
                "📌 Eslatma: FOYDA50 promokodini ishlatgan bo‘lsangizgina foyda olasiz!"
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Siz hali tasdiqlanmagansiz.\n"
                "📸 Skrinshot yuboring va admin tasdiqlashini kuting."
            )

# === ID olish ===
def get_id(message):
    user_id = message.text
    bot.send_message(
        message.chat.id,
        f"✅ ID qabul qilindi: {user_id}\n📸 Endi skrinsiz signal olmaydi, skrinshot yuboring."
    )

# === Rasmlar ===
@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    if user_status.get(message.chat.id) == "waiting_for_screenshot":
        file_id = message.photo[-1].file_id
        caption = (
            f"📸 Yangi skrinshot!\n"
            f"👤 Foydalanuvchi: {message.from_user.first_name} (@{message.from_user.username})\n"
            f"🆔 ID: {message.chat.id}"
        )
        # Kanalga yuborish
        bot.send_photo(CHANNEL_ID, file_id, caption=caption,
                       reply_markup=approval_buttons(message.chat.id))
        bot.send_message(
            message.chat.id,
            "📤 Skrinshot yuborildi. ✅ Admin tasdiqlashini kuting.\n"
            "⚠️ Linebet uchun promokod: FOYDA50 ni to‘liq kiriting!"
        )

# === Tasdiqlash tugmalari ===
def approval_buttons(user_id):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{user_id}"),
        telebot.types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}")
    )
    return markup

# === Callbacks (Admin uchun) ===
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def handle_approval(call):
    if str(call.from_user.id) != str(ADMIN_ID):
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return

    user_id = int(call.data.split("_")[1])

    if call.data.startswith("approve_"):
        user_status[user_id] = "approved"
        bot.send_message(user_id, "✅ Admin tomonidan tasdiqlandi! Endi signal olishingiz mumkin.")
        bot.edit_message_caption(
            caption="✅ Tasdiqlandi",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        user_status[user_id] = "rejected"
        bot.send_message(user_id, "❌ Skrinshot rad etildi. Iltimos qayta urinib ko‘ring.")
        bot.edit_message_caption(
            caption="❌ Rad etildi",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )

# === Flask server (Webhook) ===
server = Flask(__name__)

@server.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def index():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}{TOKEN}")
    return "Bot ishlayapti!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
