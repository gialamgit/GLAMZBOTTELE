import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import os

TOKEN = "8294241622:AAGIJuqVmk-D7IwoMXJ7GrG_g5D7LlerKzU"

ACCOUNTS_FILE = "accounts.json"
USERDATA_FILE = "user_data.json"

# ---------------------- JSON Helpers ---------------------- #
def load_json(filename, default):
    """Đọc JSON từ file, nếu chưa có thì trả về default."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    """Lưu dữ liệu Python thành file JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ---------------------- Load dữ liệu ---------------------- #
accounts = load_json(ACCOUNTS_FILE, [
    {"gmail": "acc1@gmail.com", "password": "pass1"},
    {"gmail": "acc2@gmail.com", "password": "pass2"},
    {"gmail": "acc3@gmail.com", "password": "pass3"}
])
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
    """Lưu thông tin user ra file JSON."""
    save_json(USERDATA_FILE, user_data)

# ---------------------- Command /start ---------------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)  # Lưu dạng string cho JSON
    now = datetime.now()

    # Nếu user đã nhận account
    if user_id in user_data:
        last_time = datetime.fromisoformat(user_data[user_id]["time"])

        # Nếu chưa quá 24h => không cấp mới
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

    # Nếu chưa có hoặc quá 24h => cấp tài khoản mới
    new_acc = get_new_account()
    if not new_acc:
        await update.message.reply_text("⚠️ Xin lỗi, đã hết tài khoản để cấp.")
        return

    # Lưu dữ liệu user
    user_data[user_id] = {
        "time": now.isoformat(),
        "account": new_acc
    }
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
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()