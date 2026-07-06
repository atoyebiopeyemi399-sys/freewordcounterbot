import os
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set!")
    exit(1)

# User stats
user_stats = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📊 Word Count", callback_data='wordcount_help')],
        [InlineKeyboardButton("🔤 Character Count", callback_data='charcount_help')],
        [InlineKeyboardButton("📈 My Stats", callback_data='stats')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')]
    ]
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\nWelcome to Free Word Counter Bot!\n\nSend me any text or use /wordcount command.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    user_id = str(update.effective_user.id)
    if user_id not in user_stats:
        user_stats[user_id] = {'total_words': 0, 'total_messages': 0}
    user_stats[user_id]['total_messages'] += 1

async def wordcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/wordcount", "", 1).strip()
    if not text:
        await update.message.reply_text("❌ Please provide text!\nExample: /wordcount Hello world")
        return
    
    words = len(text.split())
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    
    await update.message.reply_text(
        f"📊 **Results**\n\n📝 Words: {words}\n🔤 Characters: {chars}\n🔡 Characters (no spaces): {chars_no_space}",
        parse_mode='Markdown'
    )
    
    user_id = str(update.effective_user.id)
    if user_id in user_stats:
        user_stats[user_id]['total_words'] += words
        user_stats[user_id]['total_messages'] += 1

async def charcount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/charcount", "", 1).strip()
    if not text:
        await update.message.reply_text("❌ Please provide text!\nExample: /charcount Hello world")
        return
    
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    words = len(text.split())
    
    await update.message.reply_text(
        f"🔤 **Character Results**\n\nTotal: {chars}\nNo spaces: {chars_no_space}\nWords: {words}",
        parse_mode='Markdown'
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_stats or user_stats[user_id]['total_messages'] == 0:
        await update.message.reply_text("📊 No stats yet! Send me some text.")
        return
    
    s = user_stats[user_id]
    await update.message.reply_text(
        f"📈 **Your Stats**\n\nMessages: {s['total_messages']}\nTotal words: {s['total_words']:,}",
        parse_mode='Markdown'
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ **Free Word Counter Bot**\n\nCounts words and characters in any text.\n\nBuilt with Python ❤️",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith('/'):
        return
    
    text = update.message.text
    words = len(text.split())
    chars = len(text)
    chars_no_space = len(text.replace(" ", ""))
    
    await update.message.reply_text(
        f"📊 **Analysis**\n\nWords: {words}\nCharacters: {chars}\nChars (no spaces): {chars_no_space}",
        parse_mode='Markdown'
    )
    
    user_id = str(update.effective_user.id)
    if user_id not in user_stats:
        user_stats[user_id] = {'total_words': 0, 'total_messages': 0}
    user_stats[user_id]['total_words'] += words
    user_stats[user_id]['total_messages'] += 1

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📖 **Help**\n\nSend any text for automatic analysis\nOr use commands:\n/wordcount <text>\n/charcount <text>\n/stats\n/about",
        parse_mode='Markdown'
    )

def main():
    logger.info("🚀 Starting bot...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wordcount", wordcount))
    app.add_handler(CommandHandler("charcount", charcount))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("✅ Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
