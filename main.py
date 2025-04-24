import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# 환경변수에서 API 키와 웹훅 URL, 포트 불러오기
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL")
PORT = int(os.environ.get("PORT", 5000))
WEBHOOK_PATH = "/hook"
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"

# Flask 앱
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# 기본 경로
@app.route("/")
def home():
    return "Flask + Telegram bot is running."

# 웹훅 수신 경로
@app.route(WEBHOOK_PATH, methods=["POST"])
def receive_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# /start 명령어 처리
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 주식 분석 봇입니다. 종목명을 입력해주세요.")

# 텍스트 메시지 처리
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stock_name = update.message.text
    await update.message.reply_text(f"'{stock_name}' 분석을 준비 중입니다. 잠시만 기다려주세요...")

# 핸들러 등록
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 웹훅 설정 및 Flask 실행
async def main():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook 연결됨: {WEBHOOK_URL}")
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    asyncio.run(main())
