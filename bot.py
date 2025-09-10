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
        bot.send_message(user, "📝 Ro‘yxatdan o‘tish linki:\n👉 https://lb-aff.com/L?tag=d_4617949m_22611c_site&site=4617949&ad=22611&r=registration")

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

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

