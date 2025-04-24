
import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# 환경 변수
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL")  # 예: https://stock-bot-xxxx.onrender.com
WEBHOOK_PATH = "/hook"
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 5000))

# Flask 앱 정의
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

@app.route("/")
def home():
    return "✅ Flask 서버 작동 중!"

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
    except Exception as e:
        print(f"[ERROR] Webhook 처리 중 오류: {e}")
    return "ok", 200

# 텔레그램 핸들러
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 주식 분석 봇입니다.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"'{update.message.text}' 분석을 준비 중입니다.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask + Webhook 통합 실행
async def main():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook 연결됨: {WEBHOOK_URL}")

if __name__ == "__main__":
    import threading

    # Flask는 메인 쓰레드에서 실행
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=PORT)).start()

    # 비동기로 Webhook 등록
    asyncio.run(setup_webhook())
