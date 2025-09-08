import os
import telebot
from flask import Flask, request
import random

# === TOKEN va URL ===
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")  # oxirida '/' bo‘lishi shart

if not TOKEN or not APP_URL:
    raise ValueError("BOT_TOKEN yoki APP_URL sozlanmagan!")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# === ADMIN ID ===
ADMIN_ID = 7850048970

# === FOYDALANUVCHILAR RO‘YXATI ===
users = set()
users_with_id = set()

# === MENYU TUGMALARI ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    markup.row("📡 Signal olish 🍎", "📊 Statistika")
    markup.row("🔄 Start")
    return markup

def signal_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📡 Signal olish 🍎")
    markup.row("🔙 Orqaga")
    return markup

# === Xush kelibsiz matni ===
def welcome_text():
    return (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Quyidagi tugmalardan foydalaning 👇\n\n"
        "❗️ Diqqat! Bot faqat LINEBET uchun ishlaydi.\n"
        "1) Ro'yxatdan o'tish tugmasini bosing va sayt orqali ro'yxatdan o'ting.\n"
        "2) Promokod joyiga albatta: FOYDA50 yozing.\n"
        "3) ID raqamingizni botga kiriting.\n"
        "⚠️ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!"
    )

# === /start komandasi ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users.add(message.chat.id)
    bot.send_message(message.chat.id, welcome_text(), reply_markup=main_menu())

# === MATNLI XABARLAR ===
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

    elif message.text == "🔄 Start":
        send_welcome(message)

    elif message.text == "🔙 Orqaga":
        bot.send_message(message.chat.id, "Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

# === IDni saqlash ===
def get_id(message):
    user_id = message.text.strip()
    users_with_id.add(message.chat.id)
    bot.send_message(
        message.chat.id,
        f"✅ ID qabul qilindi: {user_id}\n📡 Endi signal olish tugmasidan foydalanishingiz mumkin.",
        reply_markup=signal_menu()
    )

# === FLASK ROUTES ===
@server.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@server.route("/", methods=['GET'])
def index():
    return "Bot ishlayapti!", 200

# === SERVERNI ISHGA TUSHURISH ===
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL + TOKEN)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))








