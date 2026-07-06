import os
import logging
import re
from datetime import datetime
from typing import Dict, Any

# Use python-telegram-bot v20.x
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    ContextTypes, 
    filters
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
    raise ValueError("TELEGRAM_BOT_TOKEN is required")

# Store user stats (in-memory, resets on restart)
user_stats: Dict[str, Dict[str, int]] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    first_name = user.first_name if user else "User"
    
    welcome_message = f"""
👋 **Hello {first_name}!**

Welcome to **Free Word Counter Bot**! 📊

I can help you count words, characters, and more in any text you send me.

**Available Commands:**
• `/start` - Show this welcome message
• `/help` - Get detailed help
• `/wordcount` - Count words in text
• `/charcount` - Count characters (with/without spaces)
• `/stats` - See your usage statistics
• `/about` - About this bot

**How to use:**
Just send me any text, and I'll reply with the word count automatically!
Or use the /wordcount command followed by your text.

Example: `/wordcount The quick brown fox jumps over the lazy dog`
    """
    
    keyboard = [
        [InlineKeyboardButton("📊 Word Count", callback_data='wordcount_help')],
        [InlineKeyboardButton("🔤 Character Count", callback_data='charcount_help')],
        [InlineKeyboardButton("📈 My Stats", callback_data='stats')],
        [InlineKeyboardButton("ℹ️ About", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Track user
    user_id = str(update.effective_user.id)
    if user_id not in user_stats:
        user_stats[user_id] = {'total_words': 0, 'total_messages': 0}
    user_stats[user_id]['total_messages'] += 1

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when /help is issued."""
    help_text = """
📖 **Help & Commands**

**Basic Usage:**
Simply send me any text message, and I'll automatically count:
• Total words
• Total characters (with spaces)
• Characters without spaces
• Lines count

**Commands:**
• `/start` - Welcome message
• `/help` - Show this help
• `/wordcount <text>` - Count words in specific text
• `/charcount <text>` - Count characters in specific text
• `/stats` - View your usage statistics
• `/about` - About this bot

**Examples:**
`/wordcount Hello world!` → Returns: 2 words
`/charcount Hello world!` → Returns: 12 characters

**Tips:**
• You can send long texts (up to 4096 characters)
• The bot counts words separated by spaces
• Punctuation is included in character count
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def word_count_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /wordcount command."""
    # Get the text after the command
    text = update.message.text.replace("/wordcount", "", 1).strip()
    
    if not text:
        await update.message.reply_text(
            "❌ Please provide some text!\n\nExample: `/wordcount The quick brown fox`",
            parse_mode='Markdown'
        )
        return
    
    # Count words
    words = text.split()
    word_count = len(words)
    
    # Count characters
    char_count = len(text)
    char_no_spaces = len(text.replace(" ", ""))
    
    # Count lines
    lines = text.split('\n')
    line_count = len(lines)
    
    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    response = f"""
📊 **Word Count Results**

📝 **Words:** {word_count}
🔤 **Characters (with spaces):** {char_count}
🔡 **Characters (without spaces):** {char_no_spaces}
📏 **Lines:** {line_count}
💬 **Sentences:** {sentence_count}
📎 **Avg chars per word:** {char_no_spaces/word_count:.1f} 
    """
    
    await update.message.reply_text(response, parse_mode='Markdown')
    
    # Update user stats
    user_id = str(update.effective_user.id)
    if user_id in user_stats:
        user_stats[user_id]['total_words'] += word_count
        user_stats[user_id]['total_messages'] += 1

async def char_count_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /charcount command."""
    # Get the text after the command
    text = update.message.text.replace("/charcount", "", 1).strip()
    
    if not text:
        await update.message.reply_text(
            "❌ Please provide some text!\n\nExample: `/charcount Hello world!`",
            parse_mode='Markdown'
        )
        return
    
    # Count everything
    char_count = len(text)
    char_no_spaces = len(text.replace(" ", ""))
    word_count = len(text.split())
    
    # Count sentences
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    response = f"""
🔤 **Character Count Results**

📝 **Total characters:** {char_count}
🔡 **Characters (no spaces):** {char_no_spaces}
📊 **Words:** {word_count}
💬 **Sentences:** {sentence_count}
📏 **Avg word length:** {char_no_spaces/word_count:.1f} chars
    """
    
    await update.message.reply_text(response, parse_mode='Markdown')
    
    # Update user stats
    user_id = str(update.effective_user.id)
    if user_id in user_stats:
        user_stats[user_id]['total_words'] += word_count
        user_stats[user_id]['total_messages'] += 1

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user statistics."""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_stats or user_stats[user_id]['total_messages'] == 0:
        await update.message.reply_text(
            "📊 **Your Statistics**\n\nYou haven't used the bot yet! Send me some text to get started.",
            parse_mode='Markdown'
        )
        return
    
    stats = user_stats[user_id]
    response = f"""
📈 **Your Statistics**

📝 **Total messages processed:** {stats['total_messages']}
📊 **Total words counted:** {stats['total_words']:,}
📏 **Average words per message:** {stats['total_words']/stats['total_messages']:.1f}

Keep using the bot to track more!
    """
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show about information."""
    about_text = """
ℹ️ **About Free Word Counter Bot**

This bot was created to help you quickly count words, characters, and more in any text.

**Features:**
• ✅ Word counting
• ✅ Character counting (with/without spaces)
• ✅ Line counting
• ✅ Sentence detection
• ✅ User statistics tracking
• ✅ Completely free

**Technical Details:**
• Built with Python and python-telegram-bot library
• Hosted on Railway
• Privacy-focused: No text is stored permanently

**Creator:** @yourusername

**Support:** For issues or suggestions, contact @yourusername
    """
    
    keyboard = [
        [InlineKeyboardButton("📝 Feedback", url="https://t.me/yourusername")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        about_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle any text message that is not a command."""
    text = update.message.text
    
    # Check if it's a command (starts with /)
    if text.startswith('/'):
        return
    
    # Count everything
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    char_no_spaces = len(text.replace(" ", ""))
    lines = text.split('\n')
    line_count = len(lines)
    
    # Detect language
    has_arabic = bool(re.search(r'[\u0600-\u06FF]', text))
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
    has_cyrillic = bool(re.search(r'[\u0400-\u04FF]', text))
    
    if has_arabic:
        language = "Arabic"
    elif has_chinese:
        language = "Chinese"
    elif has_cyrillic:
        language = "Russian/Ukrainian"
    else:
        language = "English/Latin"
    
    response = f"""
📊 **Analysis Results**

📝 **Words:** {word_count}
🔤 **Characters:** {char_count}
🔡 **Characters (no spaces):** {char_no_spaces}
📏 **Lines:** {line_count}
📎 **Avg word length:** {char_no_spaces/word_count:.1f} chars
🌐 **Language detected:** {language}
    """
    
    await update.message.reply_text(response, parse_mode='Markdown')
    
    # Update user stats
    user_id = str(update.effective_user.id)
    if user_id not in user_stats:
        user_stats[user_id] = {'total_words': 0, 'total_messages': 0}
    user_stats[user_id]['total_words'] += word_count
    user_stats[user_id]['total_messages'] += 1

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses from inline keyboards."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'wordcount_help':
        await query.edit_message_text(
            "📊 **How to Count Words**\n\n"
            "1️⃣ Send any text message\n"
            "2️⃣ Or use: `/wordcount Your text here`\n"
            "3️⃣ Or use: `/charcount Your text here`\n\n"
            "The bot will analyze your text and show detailed statistics!",
            parse_mode='Markdown'
        )
    elif data == 'charcount_help':
        await query.edit_message_text(
            "🔤 **How to Count Characters**\n\n"
            "The bot counts:\n"
            "• Total characters (including spaces)\n"
            "• Characters without spaces\n"
            "• Words\n"
            "• Sentences\n\n"
            "Try it now! Send any text or use `/charcount` command.",
            parse_mode='Markdown'
        )
    elif data == 'stats':
        # Show stats
        user_id = str(update.effective_user.id)
        if user_id not in user_stats or user_stats[user_id]['total_messages'] == 0:
            await query.edit_message_text(
                "📊 **Your Statistics**\n\nYou haven't used the bot yet! Send me some text to get started.",
                parse_mode='Markdown'
            )
            return
        stats = user_stats[user_id]
        response = f"""
📈 **Your Statistics**

📝 **Total messages processed:** {stats['total_messages']}
📊 **Total words counted:** {stats['total_words']:,}
📏 **Average words per message:** {stats['total_words']/stats['total_messages']:.1f}

Keep using the bot to track more!
        """
        await query.edit_message_text(response, parse_mode='Markdown')
    elif data == 'about':
        await query.edit_message_text(
            "ℹ️ **About Free Word Counter Bot**\n\n"
            "A free, powerful text analysis bot for Telegram.\n\n"
            "**Features:**\n"
            "• Word/Character counting\n"
            "• Line counting\n"
            "• Language detection\n"
            "• User statistics\n"
            "• Completely free!\n\n"
            "Built with ❤️ using Python",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot."""
    logger.info("🚀 Starting Free Word Counter Bot...")
    
    # Create the Application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("wordcount", word_count_command))
    app.add_handler(CommandHandler("charcount", char_count_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("about", about_command))
    
    # Add message handler for all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add callback query handler for buttons
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start the bot using polling (no webhook needed)
    logger.info("✅ Bot is running and polling for updates...")
    app.run_polling()
    
if __name__ == "__main__":
    main()
