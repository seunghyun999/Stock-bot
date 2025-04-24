import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# 환경 변수 설정
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL")
PORT = int(os.environ.get("PORT", 5000))
WEBHOOK_PATH = "/hook"
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"

# Flask 앱 생성
app = Flask(__name__)

# Telegram Application 생성
application = Application.builder().token(TOKEN).build()

# Webhook 수신 라우터
@app.route(WEBHOOK_PATH, methods=["POST"])
def receive_webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        print("✅ Webhook 수신됨")
    except Exception as e:
        print(f"❌ Webhook 처리 오류: {e}")
    return "ok"

@app.route("/")
def home():
    return "✅ Flask + Telegram 봇 작동 중입니다."

# /start 명령 처리
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("안녕하세요! 주식 분석 봇입니다. 종목명을 입력해주세요.")

# 텍스트 메시지 처리
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stock_name = update.message.text
        print(f"📩 수신된 메시지: {stock_name}")
        await update.message.reply_text(f"'{stock_name}' 분석을 준비 중입니다.")
    except Exception as e:
        print(f"❌ handle_message 오류: {e}")

# 핸들러 등록
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# 메인 실행
async def main():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook 설정 완료: {WEBHOOK_URL}")
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    asyncio.run(main())
