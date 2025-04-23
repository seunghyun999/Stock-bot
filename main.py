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
    print(">>> [Webhook] 데이터 수신됨")  # 로그
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 주식 분석 봇입니다. 종목명을 입력해주세요.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stock_name = update.message.text
        print(f"▶ 메시지 수신됨: {stock_name}")
        await update.message.reply_text(f"'{stock_name}' 분석을 준비 중입니다. 잠시만 기다려주세요...")
    except Exception as e:
        print(f"❌ 메시지 처리 중 오류: {str(e)}")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def setup_webhook():
    await application.initialize()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook 설정 완료: {WEBHOOK_URL}")

if __name__ == "__main__":
    asyncio.run(setup_webhook())
    app.run(host="0.0.0.0", port=5000)
