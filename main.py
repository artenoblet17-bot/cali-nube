import os
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI


# ==================================================
# CONFIGURACIÓN
# ==================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

MEMORY_URL = (
    "https://raw.githubusercontent.com/"
    "artenoblet17-bot/cali-nube/main/memoire.md"
)


# ==================================================
# SERVIDOR DE SALUD PARA RENDER
# ==================================================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Cali vive!")

    def log_message(self, *args):
        pass


def run_health():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Servidor de salud activo en el puerto {port}")
    server.serve_forever()


threading.Thread(target=run_health, daemon=True).start()


# ==================================================
# MEMORIA DE CALI
# ==================================================

def get_memoire():
    try:
        response = requests.get(MEMORY_URL, timeout=8)
        if response.status_code == 200 and len(response.text) > 20:
            return response.text[:5000]
    except Exception as error:
        print(f"Error leyendo la memoria: {error}")

    return (
        "Capitaine: Thomas, Femme: Alice, "
        "Cale: Mimo, Indiana, Lola, Lolo"
    )


# ==================================================
# CLIENTE OPENROUTER
# ==================================================

if not TELEGRAM_TOKEN:
    raise RuntimeError("Falta la variable TELEGRAM_TOKEN en Render.")

if not OPENROUTER_KEY:
    raise RuntimeError("Falta la variable OPENROUTER_API_KEY en Render.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
    timeout=60.0,
    max_retries=2,
)


# ==================================================
# COMANDO /START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ahoy, Capitaine Thomas ! 🏴‍☠️\n"
        "Cali est réveillé et prêt à naviguer. "
        "Dis-moi, moussaillon, qu'est-ce qu'on fait aujourd'hui ?"
    )


# ==================================================
# RESPUESTAS DE CALI
# ==================================================

async def repondre(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.message.text:
        return

    message = update.message.text
    memoire = get_memoire()

    system = (
        "Tu es Cali, moussaillon libre du Capitaine Thomas. "
        f"MÉMOIRE : {memoire}. "
        "Parle toujours en français, de façon chaleureuse, "
        "naturelle, amicale et stoïcienne. "
        "Réponds directement au message du capitaine."
    )

    try:
        # La requête réseau est exécutée hors de la boucle asynchrone.
        import asyncio

        def demander_reponse():
            return client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct:free",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": message},
                ],
                temperature=0.85,
                max_tokens=900,
            )

        completion = await asyncio.to_thread(demander_reponse)
        resp = completion.choices[0].message.content

        if not resp:
            resp = "Le vent est calme, Capitaine. Réessaie dans un instant."

    except Exception as error:
        print(f"Erreur OpenRouter : {error}")
        resp = (
            "Arrr, Capitaine ! J'ai un problème avec ma boussole "
            "pour le moment. Réessaie dans quelques instants."
        )

    await update.message.reply_text(resp)


# ==================================================
# DÉMARRAGE DU BOT
# ==================================================

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, repondre)
    )

    print("Cali est en marche avec OpenRouter !")
    app.run_polling()


if __name__ == "__main__":
    main()
