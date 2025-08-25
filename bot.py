import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta

# Lấy TOKEN từ biến môi trường
TOKEN = os.getenv("TOKEN")

ACCOUNTS_FILE = "accounts.json"
USERDATA_FILE = "user_data.json"

# ---------------------- JSON Helpers ---------------------- #
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ---------------------- Load dữ liệu ---------------------- #
accounts = load_json(ACCOUNTS_FILE, [])
user_data = load_json(USERDATA_FILE, {})

# ---------------------- Helper Functions ---------------------- #
def mask(text: str, visible: int = 1) -> str:
    """Che ký tự, chỉ giữ visible ký tự đầu."""
    if len(text) <= visible:
        return "*" * len(text)
    return text[:visible] + "*" * (len(text) - visible)

def get_new_account():
    """Lấy tài khoản mới và lưu lại."""
    global accounts
    if accounts:
        acc = accounts.pop(0)
        save_json(ACCOUNTS_FILE, accounts)
        return acc
    return None

def save_user_data():
    save_json(USERDATA_FILE, user_data)

# ---------------------- Command /start ---------------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    now = datetime.now()

    # Kiểm tra user đã nhận account chưa
    if user_id in user_data:
        last_time = datetime.fromisoformat(user_data[user_id]["time"])
        if now - last_time < timedelta(hours=24):
            acc = user_data[user_id]["account"]
            wait_hours = 24 - (now - last_time).seconds // 3600
            await update.message.reply_text(
                f"🚫 Bạn đã nhận tài khoản hôm nay.\n"
                f"⏳ Vui lòng đợi {wait_hours} giờ nữa.\n\n"
                f"📧 Gmail: {mask(acc['gmail'], 1)}\n"
                f"🔒 Mật khẩu: {mask(acc['password'], 1)}"
            )
            return

    # Cấp mới
    new_acc = get_new_account()
    if not new_acc:
        await update.message.reply_text("⚠️ Xin lỗi, đã hết tài khoản để cấp.")
        return

    # Lưu lại
    user_data[user_id] = {"time": now.isoformat(), "account": new_acc}
    save_user_data()

    msg = (
        "-----📌 Thông Tin 📌-----\n"
        f"👤 Tên: {user.full_name}\n"
        f"⏰ Truy cập: {now.strftime('%H:%M:%S %d-%m-%Y')}\n\n"
        "-----📂 Danh Mục Tài Khoản-----\n"
        f"📧 Gmail: {mask(new_acc['gmail'], 1)}\n"
        f"🔒 Mật khẩu: {mask(new_acc['password'], 1)}"
    )
    await update.message.reply_text(msg)

# ---------------------- Main ---------------------- #
def main():
    if not TOKEN:
        print("❌ Chưa set TOKEN. Hãy set biến môi trường TOKEN trước khi chạy!")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()