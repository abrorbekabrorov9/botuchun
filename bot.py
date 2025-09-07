import os
import telebot
import logging
import random

# === BOT TOKEN (Railway Environment Variable dan) ===
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable topilmadi!")

bot = telebot.TeleBot(TOKEN)

# === LOGGING ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# === ADMIN ID ===
ADMIN_ID = 7850048970  # faqat sening IDing

# === Foydalanuvchilarni saqlash ===
user_ids_db = set()

# === MENYU ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    markup.row("📡🍎 Signal olish")
    return markup

# === /START ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Quyidagi tugmalardan foydalaning 👇\n\n"
        "❗️ Diqqat! Bot faqat LINEBET uchun ishlaydi!\n"
        "1) \"Ro'yxatdan o'tish\" tugmasini bosing va sayt orqali ro'yxatdan o'ting.\n"
        "2) Promokod joyiga albatta: **FOYDA50** yozing.\n"
        "3) ID raqamingizni botga kiriting.\n"
        "⚠️ Aks holda bot sizga noto‘g‘ri signal ko‘rsatadi!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# === Matnli tugmalar ===
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.text == "📝 Ro'yxatdan o'tish":
        bot.send_message(
            message.chat.id,
            "📝 Ro'yxatdan o'tish uchun havolalar:\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration\n"
            "👉 https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803\n\n"
            "‼️ Diqqat! Promokod maydoniga **FOYDA50** kiriting, aks holda bot signal bermaydi!"
        )

    elif message.text == "▶️ Davom etish":
        msg = bot.send_message(message.chat.id, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, get_id)

    elif message.text == "📡🍎 Signal olish":
        if str(message.chat.id) in user_ids_db:
            random_number = random.randint(1, 5)
            bot.send_message(message.chat.id, f"📡🍎 Signal: {random_number}")
        else:
            bot.send_message(
                message.chat.id,
                "⛔ Avval ID raqamingizni kiriting! \"▶️ Davom etish\" tugmasidan foydalaning."
            )

# === ID olish ===
def get_id(message):
    user_id = message.text.strip()
    user_ids_db.add(str(message.chat.id))  # foydalanuvchi chat.id saqlanadi
    bot.send_message(
        message.chat.id,
        f"✅ ID qabul qilindi: {user_id}\n"
        f"📡 Endi 'Signal olish' tugmasidan foydalanishingiz mumkin."
    )

# === /stats faqat ADMIN uchun ===
@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.chat.id == ADMIN_ID:
        count = len(user_ids_db)
        bot.send_message(message.chat.id, f"👥 Hozirgacha ro‘yxatdan o‘tgan foydalanuvchilar soni: {count} ta")
    else:
        bot.send_message(message.chat.id, "⛔ Bu buyruq faqat admin uchun.")

# === BOT ISHGA TUSHURISH ===
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik yuz berdi: {e}")




