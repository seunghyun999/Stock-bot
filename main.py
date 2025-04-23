import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = f"{os.getenv('WEBHOOK_BASE_URL')}/hook"

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

@app.route("/")
def home():
    return "Flask + Telegram bot is running."

@app.route("/hook", methods=["POST"])
def webhook_handler():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    print(">>> [Webhook] 데이터 수신됨")
    return "ok"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 주식 분석 봇입니다. 종목명을 입력해주세요.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"'{update.message.text}' 분석 준비 중입니다.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def run():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook 설정 완료: {WEBHOOK_URL}")
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    asyncio.run(run())
