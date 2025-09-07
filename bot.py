import os
import telebot
import logging
import random  # random sonlar uchun

# === BOT TOKEN (Railway Environment Variable dan) ===
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable topilmadi!")

bot = telebot.TeleBot(TOKEN)

# === LOGGING sozlamalari ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# === MENYU TUGMALARI ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📝 Ro'yxatdan o'tish", "▶️ Davom etish")
    markup.row("🔔 Signal olish")  # signal tugmasi qo‘shildi
    return markup

# === /START BUYRUG'I ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Hurmatli foydalanuvchi!\n\n"
        "Botdan foydalanish uchun avval ro‘yxatdan o‘ting.\n"
        "Agar promokod: FOYDA50 ishlatmasangiz yoki ID noto‘g‘ri bo‘lsa, signal bermaydi!"
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
            "👉 Linebet dasturi: https://lb-aff.com/L?tag=d_4617949m_66803c_apk1&site=4617949&ad=66803"
        )

    elif message.text == "▶️ Davom etish":
        msg = bot.send_message(message.chat.id, "🔑 ID raqamingizni kiriting:")
        bot.register_next_step_handler(msg, get_id)

    elif message.text == "🔔 Signal olish":
        random_number = random.randint(1, 5)  # 1 dan 5 gacha tasodifiy son
        bot.send_message(message.chat.id, f"🍎 Signal: {random_number}")

# === ID OLIB ===
def get_id(message):
    user_id = message.text
    bot.send_message(message.chat.id, f"✅ ID qabul qilindi: {user_id}\n📡 Endi signal olish mumkin.")

# === BOTNI ISHGA TUSHURISH ===
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Botni ishga tushirishda xatolik yuz berdi: {e}")




