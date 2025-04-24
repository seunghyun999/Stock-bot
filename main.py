import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = "/hook"
WEBHOOK_URL = f"{os.getenv('WEBHOOK_BASE_URL')}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

@app.route(WEBHOOK_PATH, methods=["POST"])
def receive_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "✅ Flask + Telegram Webhook 서버 정상 작동 중!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 주식 분석 봇입니다. 종목명을 입력해주세요.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stock_name = update.message.text
    await update.message.reply_text(f"'{stock_name}' 분석을 준비 중입니다. 잠시만 기다려주세요...")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def run():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook 설정 완료: {WEBHOOK_URL}")
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    asyncio.run(run())
