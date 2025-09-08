import os
import telebot
from flask import Flask, request
import random

# === TOKEN va URL ===
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")  # Railway Variables ichida
if not TOKEN or not APP_URL:
    raise ValueError("BOT_TOKEN yoki APP_URL topilmadi!")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === Asosiy menyu ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    markup.row("🔔 Signal olish")
    return markup

# === Flask route (webhook uchun) ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# === /start komandasi ===
@bot.message_handler(commands=["start"])
def send_welcome(message):
    welcome_text = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Botdan foydalanish uchun avval ro‘yxatdan o‘ting.\n"
        "Agar promokod: *FOYDA50* ishlatmasangiz yoki ID noto‘g‘ri bo‘lsa, signal bermaydi!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# === Matnli xabarlar ===
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            message.chat.id,
            "📝 Ro'yxatdan o'tish uchun havolalar:\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 Linebet dasturi: https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803",
            reply_markup=main_menu()
        )

    elif message.text == "▶️ Davom etish":
        msg = bot.send_message(message.chat.id, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, get_id)

    elif message.text == "🔔 Signal olish":
        random_number = random.randint(1, 5)
        bot.send_message(message.chat.id, f"🍎 Signal: {random_number}", reply_markup=main_menu())

# === ID olish ===
def get_id(message):
    user_id = message.text
    bot.send_message(
        message.chat.id,
        f"✅ ID qabul qilindi: {user_id}\n📡 Endi signal olish mumkin.",
        reply_markup=main_menu()
    )

# === Webhookni o‘rnatish ===
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
