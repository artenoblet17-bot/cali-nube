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
    resp = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct:free",
        messages=[{"role": "user", "content": texto}]
    )
    await update.message.reply_text(resp.choices[0].message.content)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Flask va en segundo plano (así Render no te lo reinicia)
    threading.Thread(target=run_flask, daemon=True).start()

    # El bot va en el hilo principal (así no da el error de set_wakeup_fd)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responde))
    print("Bot iniciado...")
    app.run_polling(drop_pending_updates=True)
