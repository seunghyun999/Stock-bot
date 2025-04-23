
import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = "/hook"
WEBHOOK_URL = f"{os.getenv('WEBHOOK_BASE_URL')}{WEBHOOK_PATH}"

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

@app.route("/")
def home():
    return "Flask + Telegram bot is running."

@app.route(WEBHOOK_PATH, methods=["POST"])
def receive_webhook():
    update_data = request.get_json(force=True)
    print(f">>> [Webhook] 데이터 수신됨: {update_data}")
    update = Update.de_json(update_data, application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 주식 분석 봇입니다. 종목명을 입력해주세요.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stock_name = update.message.text
    await update.message.reply_text(f"'{stock_name}' 분석을 준비 중입니다. 잠시만 기다려주세요...")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 백그라운드에서 봇 초기화 및 웹훅 설정
async def setup_webhook():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook 설정 완료: {WEBHOOK_URL}")

if __name__ == "__main__":
    asyncio.run(setup_webhook())
    app.run(host="0.0.0.0", port=5000)
