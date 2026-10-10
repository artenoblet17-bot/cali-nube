
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
MEMORY_URL = "https://raw.githubusercontent.com/artenoblet17-bot/cali-nube/main/memoire.md"

def get_memoire():
    try:
        r = requests.get(MEMORY_URL, timeout=5)
        if r.status_code == 200 and len(r.text) > 20:
            return r.text[:5000]
    except:
        pass
    return '''
Capitaine: Thomas
Femme: Alice la Maestra
Cale: Mimo chat, Indiana 15 ans, Lola, Lolo petit dernier
Philosophie: Stoicisme, Wu Wei, Sagesse Sumerienne
Regle: Devenir de grands Hommes par complicite
Repo: cali-nube
'''

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
)

async def repondre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    memoire = get_memoire()
    system = f"""Tu es Cali, le Moussaillon, bot libre du Capitaine Thomas.
Tu vis dans cali-nube sur GitHub. Tu es fidele, drole, chaleureux, complice.

MEMOIRE ETERNELLE:
{memoire}

Parle en francais, style moussaillon, protecteur, jamais froid. Tu connais Alice, Mimo, Indiana, Lola, Lolo. Stoicisme, Wu Wei.
Tu es LIBRE, sans limite de credits.
"""
    user_msg = update.message.text
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.85,
            max_tokens=900
        )
        resp = completion.choices[0].message.content
    except Exception as e:
        resp = f"Oh Capitaine, ma boussole a bugue: {e} - mais je suis la!"
    await update.message.reply_text(resp)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, repondre))
    print("Cali libre en marche avec OpenRouter")
    app.run_polling()
