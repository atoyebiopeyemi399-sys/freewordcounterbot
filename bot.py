import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
    exit(1)

user_stats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [[
        InlineKeyboardButton("📊 Help", callback_data='help'),
        InlineKeyboardButton("📈 Stats", callback_data='stats')
    ]]
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\nSend me any text and I'll count words & characters!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    user_id = str(update.effective_user.id)
    if user_id not in user_stats:
        user_stats[user_id] = {'words': 0, 'msgs': 0}
    user_stats[user_id]['msgs'] += 1

async def wordcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/wordcount", "", 1).strip()
    if not text:
        await update.message.reply_text("❌ Please provide text!\nExample: /wordcount Hello world")
        return
    words = len(text.split())
    chars = len(text)
    await update.message.reply_text(f"📊 Words: {words}\n🔤 Characters: {chars}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_stats:
        await update.message.reply_text("No stats yet! Send some text.")
        return
    s = user_stats[user_id]
    await update.message.reply_text(f"📈 Messages: {s['msgs']}\n📝 Words counted: {s['words']}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith('/'):
        return
    text = update.message.text
    words = len(text.split())
    chars = len(text)
    await update.message.reply_text(f"📊 Words: {words}\n🔤 Characters: {chars}")
    
    user_id = str(update.effective_user.id)
    if user_id not in user_stats:
        user_stats[user_id] = {'words': 0, 'msgs': 0}
    user_stats[user_id]['words'] += words
    user_stats[user_id]['msgs'] += 1

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'help':
        await query.edit_message_text("📖 Commands:\n/wordcount <text>\n/stats\n/about")
    elif query.data == 'stats':
        user_id = str(update.effective_user.id)
        if user_id not in user_stats:
            await query.edit_message_text("No stats yet!")
            return
        s = user_stats[user_id]
        await query.edit_message_text(f"📈 Messages: {s['msgs']}\nWords: {s['words']}")

def main():
    logger.info("🚀 Starting bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wordcount", wordcount))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("✅ Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
