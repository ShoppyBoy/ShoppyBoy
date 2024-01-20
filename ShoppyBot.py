import logging
import asyncio
import time
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext, Updater
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot
application = ApplicationBuilder().token("6953246709:AAEJyKK44ubgZFMaILwDKZROiLaYOT_AroA").build()

# Store bot screaming status
screaming = True

# Menu text and button configuration
FIRST_MENU = "<b>Menu 1</b>\n\nA beautiful menu with a shiny inline button."
SECOND_MENU = "<b>Menu 2</b>\n\nA better menu with even more shiny inline buttons."
NEXT_BUTTON = "Next"
BACK_BUTTON = "Back"
TUTORIAL_BUTTON = "Tutorial"

# Build keyboards
FIRST_MENU_MARKUP = InlineKeyboardMarkup([[InlineKeyboardButton(NEXT_BUTTON, callback_data=NEXT_BUTTON)]])
SECOND_MENU_MARKUP = InlineKeyboardMarkup([
    [InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
    [InlineKeyboardButton(TUTORIAL_BUTTON, url="https://core.telegram.org/bots/api")]
])

# Define your command and message handlers
async def scream(update: Update, context: CallbackContext) -> None:
    global screaming
    screaming = True

async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I am ShoppyBot, your personal shopping assistant. What would you like to buy today?")

async def whisper(update: Update, context: CallbackContext) -> None:
    global screaming
    screaming = False

async def menu(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(update.effective_chat.id, FIRST_MENU, parse_mode=ParseMode.HTML, reply_markup=FIRST_MENU_MARKUP)

async def echo(update: Update, context: CallbackContext) -> None:
    if screaming and update.message.text:
        await context.bot.send_message(update.effective_chat.id, update.message.text.upper(), entities=update.message.entities)
    else:
        await update.message.copy(update.effective_chat.id)

async def button_tap(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    text = markup = None

    if data == NEXT_BUTTON:
        text = SECOND_MENU
        markup = SECOND_MENU_MARKUP
    elif data == BACK_BUTTON:
        text = FIRST_MENU
        markup = FIRST_MENU_MARKUP

    await query.answer()
    await query.edit_message_text(text=text, parse_mode=ParseMode.HTML, reply_markup=markup)

async def quit(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(update.effective_chat.id, "Bye!")
    await application.updater.stop()
    await application.stop()
    await application.shutdown()

async def read(update: Update, context: CallbackContext) -> None:
    # Initialize webdriver
    browser = webdriver.Chrome()
    browser.get("https://shopee.sg/Anchor-Strong-Beer-Can-24-x-490ml-i.91799978.4714216766?sp_atk=ed568bb5-2935-4f92-8b40-fd15453d5043&xptdk=ed568bb5-2935-4f92-8b40-fd15453d5043")
    linkbar = browser.find_element_by_id('source')
    linkbar.send_keys(context.args) 
    linkbar.send_keys(Keys.ENTER)
    time.sleep(100)
    context.bot.send_message(chat_id=update.message.chat_id, text=browser.current_url)
    
    
    
# Main function to run the bot
async def main() -> None:

    # Register handlers
    application.add_handler(CommandHandler("scream", scream))
    application.add_handler(CommandHandler("whisper", whisper))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button_tap))
    application.add_handler(MessageHandler(~filters.Command(), echo))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('quit', quit))
    application.add_handler(CommandHandler('read', read))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Create a never-set event to keep the loop running
    stop = asyncio.Event()
    await stop.wait()  # This will block indefinitely until stop.set() is called

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
