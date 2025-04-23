
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import threading

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_PATH = "/hook"
WEBHOOK_URL = f"{os.getenv('WEBHOOK_BASE_URL')}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

@app.route("/")
def home():
    return "Flask + Telegram bot is running."

@app.route(WEBHOOK_PATH, methods=["POST"])
def receive_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/analyze", methods=["POST"])
async def analyze():
    data = request.json
    stock_name = data.get("stock", "종목명 없음")
    return jsonify({
        "response": f"{stock_name}에 대한 분석 결과입니다. (예시)"
    })

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 주식 분석 봇입니다. 종목명을 입력해주세요.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stock_name = update.message.text
    await update.message.reply_text("분석 요청 접수 완료! 잠시만 기다려주세요.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def setup():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook 설정 완료: {WEBHOOK_URL}")

if __name__ == "__main__":
    def run_flask():
        app.run(host="0.0.0.0", port=PORT)

    def run_bot():
        asyncio.run(setup())

    threading.Thread(target=run_bot).start()
    run_flask()
