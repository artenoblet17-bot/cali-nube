import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY
)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot cali-libre funcionando!"

async def responde(update, context):
    texto = update.message.text
    try:
        resp = client.chat.completions.create(
            model="google/gemma-2-9b-it:free",
            messages=[{"role": "user", "content": texto}]
        )
        await update.message.reply_text(resp.choices[0].message.content)
    except Exception as e:
        print(f"Error OpenRouter: {e}")
        await update.message.reply_text("Estoy saturado 10 segundos capi, vuelve a probar")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responde))
    print("Bot iniciado...")
    app.run_polling(drop_pending_updates=True)
    
