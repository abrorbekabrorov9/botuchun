import os
import telebot
import logging
import random
from flask import Flask, request

# === ENVIRONMENT VARIABLES ===
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")

if not TOKEN or not APP_URL:
    raise ValueError("BOT_TOKEN yoki APP_URL topilmadi!")

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

# === LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === ADMIN VA KANAL ID ===
ADMIN_ID = 7850048970
CHANNEL_ID = -1003045379122   # yopiq kanal ID sini shu yerga yozdik

# === USER DATA ===
users = {}  # {chat_id: {"confirmed": False, "id": None}}

# === MENYU ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    markup.row("📡 Signal olish 🍎", "📊 Statistika")
    return markup

# === START ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users.setdefault(message.chat.id, {"confirmed": False, "id": None})
    welcome_text = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Quyidagi tugmalardan foydalaning 👇\n\n"
        "❗️ Diqqat! Bot faqat LINEBET uchun ishlaydi.\n"
        "👉 Promokod joyiga albatta: FOYDA50 yozing.\n"
        "⚠️ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# === TEXT HANDLER ===
@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_message(message):
    chat_id = message.chat.id

    if message.text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            chat_id,
            "📝 Ro'yxatdan o'tish uchun havolalar:\n\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n"
            "👉 https://uzb.bonus-linebet.com/foyda50\n\n"
            "ℹ️ O‘zingizga qulay bo‘lganidan ro‘yxatdan o‘ting."
        )

    elif message.text == "▶️ Davom etish":
        msg = bot.send_message(chat_id, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, get_id)

    elif message.text == "📡 Signal olish 🍎":
        user = users.get(chat_id)
        if user and user.get("confirmed"):
            random_number = random.randint(1, 5)
            signal_text = (
                f"📡 Signal: {random_number} 🍎\n\n"
                "⚠️ Eslatma!\n"
                "👉 Bot faqat LINEBET uchun ishlaydi.\n"
                "👉 Promokod joyiga albatta *FOYDA50* yozing.\n"
                "❌ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!"
            )
            bot.send_message(chat_id, signal_text)
        else:
            bot.send_message(chat_id, "⛔ Siz hali tasdiqlanmagansiz! Avval skrinshot yuboring.")

    elif message.text == "📊 Statistika":
        if chat_id == ADMIN_ID:
            total_users = len(users)
            confirmed_users = sum(1 for u in users.values() if u.get("confirmed"))
            bot.send_message(
                chat_id,
                f"📊 Bot foydalanuvchilari soni: {total_users}\n"
                f"✅ Tasdiqlanganlar soni: {confirmed_users}"
            )
        else:
            bot.send_message(chat_id, "❌ Bu bo‘lim faqat admin uchun!")

# === ID QABUL QILISH ===
def get_id(message):
    chat_id = message.chat.id
    user_id = message.text.strip()
    users.setdefault(chat_id, {"confirmed": False, "id": None})
    users[chat_id]["id"] = user_id
    bot.send_message(chat_id, f"✅ ID qabul qilindi: {user_id}\n📸 Endi skrinshot yuboring.")

# === SKRINSHOT ===
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    users.setdefault(chat_id, {"confirmed": False, "id": None})

    # Kanalga yuborish
    caption = f"👤 UserID: {chat_id}\n📸 Skrinshot yubordi."
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{chat_id}"),
        telebot.types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{chat_id}")
    )

    file_id = message.photo[-1].file_id
    bot.send_photo(CHANNEL_ID, file_id, caption=caption, reply_markup=markup)
    bot.send_message(chat_id, "📨 Skrinshot yuborildi, admin tekshiradi.")

# === CALLBACK HANDLER (ADMIN TUGMALARI) ===
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if str(call.from_user.id) != str(ADMIN_ID):
        bot.answer_callback_query(call.id, "⛔ Faqat admin tasdiqlay oladi.")
        return

    action, user_id = call.data.split("_")
    user_id = int(user_id)

    if action == "confirm":
        users[user_id]["confirmed"] = True
        bot.send_message(user_id, "✅ Skrinshotingiz tasdiqlandi!\nEndi signal olishingiz mumkin.")
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=call.message.caption + "\n\n✅ Tasdiqlandi"
        )

    elif action == "reject":
        users[user_id]["confirmed"] = False
        bot.send_message(user_id, "❌ Skrinshotingiz tasdiqlanmadi.\nIltimos, qayta yuboring.")
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption=call.message.caption + "\n\n❌ Rad etildi"
        )

# === WEBHOOK ===
@server.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def index():
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}{TOKEN}")
    return "Webhook ishlayapti!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

