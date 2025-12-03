from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import config

# Load database
try:
    with open("database.json", "r") as f:
        database = json.load(f)
except:
    database = {}

def build_buttons(options, back=False):
    keyboard = []
    for o in options:
        keyboard.append([InlineKeyboardButton(o, callback_data=o)])
    if back:
        keyboard.append([InlineKeyboardButton("⬅️ Go Back", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = build_buttons(list(database.keys()))
    await update.message.reply_text("Welcome! Select a category:", reply_markup=keyboard)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Go back
    if data == "back":
        keyboard = build_buttons(list(database.keys()))
        await query.edit_message_text("Welcome! Select a category:", reply_markup=keyboard)
        context.user_data.clear()
        return

    # Category level
    if data in database:
        keyboard = build_buttons(list(database[data].keys()), back=True)
        await query.edit_message_text(f"Select year in {data}:", reply_markup=keyboard)
        context.user_data['current_category'] = data
        return

    # Year level
    if 'current_category' in context.user_data and data in database[context.user_data['current_category']]:
        category = context.user_data['current_category']
        keyboard = build_buttons(list(database[category][data].keys()), back=True)
        context.user_data['current_year'] = data
        await query.edit_message_text(f"Select semester in {data}:", reply_markup=keyboard)
        return

    # Semester level
    if (
        'current_category' in context.user_data and
        'current_year' in context.user_data and
        data in database[context.user_data['current_category']][context.user_data['current_year']]
    ):
        category = context.user_data['current_category']
        year = context.user_data['current_year']
        keyboard = build_buttons(list(database[category][year][data].keys()), back=True)
        context.user_data['current_semester'] = data
        await query.edit_message_text(f"Select course in {data}:", reply_markup=keyboard)
        return

    # Course → File level
    if (
        'current_category' in context.user_data and
        'current_year' in context.user_data and
        'current_semester' in context.user_data
    ):
        category = context.user_data['current_category']
        year = context.user_data['current_year']
        semester = context.user_data['current_semester']
        if data in database[category][year][semester]:
            file_id = database[category][year][semester][data]
            await query.message.reply_document(file_id)
            return

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start to open the menu.")

app = ApplicationBuilder().token(config.BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CallbackQueryHandler(button))

print("Bot is running...")
app.run_polling()
