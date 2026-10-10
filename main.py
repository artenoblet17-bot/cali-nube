import os, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI
TELEGRAM_TOKEN=os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY=os.getenv("OPENROUTER_API_KEY")
MEMORY_URL="https://raw.githubusercontent.com/artenoblet17-bot/cali-nube/main/memoire.md"
def get_memoire():
    try:
        r=requests.get(MEMORY_URL,timeout=5)
        if r.status_code==200 and len(r.text)>20: return r.text[:5000]
    except: pass
    return "Capitaine: Thomas, Femme: Alice, Cale: Mimo, Indiana 15 ans, Lola, Lolo"
client=OpenAI(base_url="https://openrouter.ai/api/v1",api_key=OPENROUTER_KEY)
async def repondre(update:Update,context:ContextTypes.DEFAULT_TYPE):
    memoire=get_memoire()
    system=f"Tu es Cali, Moussaillon libre du Capitaine Thomas. MEMOIRE: {memoire}. Parle francais, chaleureux, complice, stoicien Wu Wei."
    try:
        c=client.chat.completions.create(model="meta-llama/llama-3.1-8b-instruct:free",messages=[{"role":"system","content":system},{"role":"user","content":update.message.text}],temperature=0.85,max_tokens=900)
        resp=c.choices[0].message.content
    except Exception as e: resp=f"Bug boussole: {e}"
    await update.message.reply_text(resp)
if __name__=="__main__":
    app=ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,repondre))
    print("Cali libre en marche avec OpenRouter")
    app.run_polling()
