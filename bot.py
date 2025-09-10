import os
import telebot
import logging
import random
from flask import Flask, request

# === TOKEN & URL ===
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")

if not TOKEN or not APP_URL:
    raise ValueError("BOT_TOKEN yoki APP_URL topilmadi!")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# === LOGGING ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# === ADMIN ID ===
ADMIN_ID = 7850048970

# === Foydalanuvchilarni saqlash ===
users = set()
users_with_id = set()

# === MENYU TUGMALARI ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    markup.row("📡 Signal olish 🍎")
    markup.row("📊 Statistika", "/start")  # 👉 bu yerda /start tugmasi qo‘shildi
    return markup

def signal_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📡 Signal olish 🍎")
    markup.row("🔙 Orqaga", "/start")
    return markup

# === /START ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users.add(message.chat.id)
    welcome_text = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Quyidagi tugmalardan foydalaning 👇\n\n"
        "❗️ Diqqat! Bot faqat LINEBET uchun ishlaydi.\n"
        "1) Ro'yxatdan o'tish tugmasini bosing va sayt orqali ro'yxatdan o'ting.\n"
        "2) Promokod joyiga albatta: FOYDA50 yozing.\n"
        "3) ID raqamingizni botga kiriting.\n"
        "⚠️ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# === Matnli xabarlar ===
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            message.chat.id,
            "📝 Ro'yxatdan o'tish uchun havolalar:\n\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n\n"
            "❗️ Diqqat: Ro‘yxatdan o‘tayotganda PROMOKOD joyiga albatta *FOYDA50* yozing!\n"
            "Aks holda bot sizga aniq signal ko‘rsatmaydi."
        )

    elif message.text == "▶️ Davom etish":
        msg = bot.send_message(message.chat.id, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, get_id)

    elif message.text == "📡 Signal olish 🍎":
        if message.chat.id in users_with_id:
            random_number = random.randint(1, 5)
            signal_text = (
                f"📡 Signal: {random_number} 🍎\n\n"
                "⚠️ Eslatma!\n"
                "👉 Bot faqat LINEBET uchun ishlaydi.\n"
                "👉 Promokod joyiga albatta *FOYDA50* yozing.\n"
                "❌ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!"
            )
            bot.send_message(message.chat.id, signal_text)
        else:
            bot.send_message(message.chat.id, "❌ Avval ID raqamingizni kiriting!")

    elif message.text == "📊 Statistika":
        if message.chat.id == ADMIN_ID:
            bot.send_message(
                message.chat.id,
                f"📊 Bot foydalanuvchilari soni: {len(users)}\n"
                f"✅ ID kiritganlar soni: {len(users_with_id)}"
            )
        else:
            bot.send_message(message.chat.id, "❌ Bu bo‘lim faqat admin uchun!")

    elif message.text == "🔙 Orqaga":
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

    elif message.text.startswith("/send"):
        if message.chat.id == ADMIN_ID:
            text = message.text.replace("/send", "").strip()
            if text:
                sent = 0
                for uid in users:
                    try:
                        bot.send_message(uid, text)
                        sent += 1
                    except:
                        pass
                bot.send_message(message.chat.id, f"✅ Xabar {sent} ta foydalanuvchiga yuborildi.")
            else:
                bot.send_message(message.chat.id, "❌ Matn kiriting: /send Salom hammaga!")
        else:
            bot.send_message(message.chat.id, "❌ Sizda bu buyruqni ishlatish huquqi yo‘q!")

    elif message.text == "/start":
        send_welcome(message)  # 👉 /start tugmasi bosilganda ham qayta welcome chiqadi

# === ID olish ===
def get_id(message):
    user_id = message.text.strip()
    users_with_id.add(message.chat.id)
    bot.send_message(
        message.chat.id,
        f"✅ ID qabul qilindi: {user_id}\n📡 Endi signal olish tugmasidan foydalanishingiz mumkin.",
        reply_markup=signal_menu()
    )

# === WEBHOOK ===
@server.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.stream.read().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}{TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


