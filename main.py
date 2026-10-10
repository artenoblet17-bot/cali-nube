import os
import threading
import asyncio
import telegram
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

# Lista de modelos gratis, en orden. Si falla uno, prueba el siguiente
MODELOS_GRATIS = [
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2-7b-instruct:free",
]

async def responde(update, context):
    texto = update.message.text
    last_error = ""
    for modelo in MODELOS_GRATIS:
        try:
            print(f"Probando modelo: {modelo}")
            resp = client.chat.completions.create(
                model=modelo,
                messages=[{"role": "user", "content": texto}]
            )
            await update.message.reply_text(resp.choices[0].message.content)
            return # si funciona, salimos
        except Exception as e:
            last_error = str(e)
            print(f"Fallo {modelo}: {e}")
            continue

    # Si fallan todos
    await update.message.reply_text(f"Los modelos gratis están saturados ahora mismo. Error: {last_error[:200]}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

async def delete_webhook():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(delete_webhook())
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responde))
    print("Bot iniciado...")
    app.run_polling(drop_pending_updates=True)
