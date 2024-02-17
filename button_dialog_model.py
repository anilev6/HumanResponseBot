from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import random

from settings import TG_BOT_TOKEN
from mylogging import logger, time_log_decorator


# Define states for the conversation
INPUT_TEXT, SHOW_MENU = range(2)
INPUT_TEXT_MESSAGE = "Please write something:"
BUTTON_TEXT = "Click Me"
KEYBOAD_TEXT = "Please choose:"
BUTTON_REPLY_MESSAGE = "Received your input: {}"
MUTE_TEXT = "🏀"


def get_mute_text_emoji():
    # emoji_list = [
    #     "🍏", "🍎", "🍐", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍈", "🍒", "🍑", "🥭", "🍍", "🥥", "🥝", 
    #     "🍅", "🍆", "🥑", "🫛", "🥦", "🥬", "🥒", "🌶", "🫑", "🌽", "🥕", "🫒", "🧄", "🧅", "🥔", "🍠", "🫚", 
    #     "🥐", "🥯", "🍞", "🥖", "🥨", "🧀", "🥚", "🍳", "🧈", "🥞", "🧇", "🥓", "🥩", "🍗", "🍖", "🌭", "🍔", 
    #     "🍟", "🍕", "🥪", "🥙", "🧆", "🌮", "🌯", "🫔", "🥗", "🥘", "🫕", "🥫", "🍝", "🍜", "🍲", "🍛", "🥟", 
    #     "🍤", "🍙", "🍥", "🍘", "🍢", "🍡", "🍧", "🍨", "🍦", "🍿", "🍬", "🍭", "🍮", "🍫", "🍦", "🥧", "🧁", 
    #     "🍰", "🎂", "🍼", "🍪", "🌰", "🥜", "🍩", "🍯"
    # ]
    # return random.choice(emoji_list)
    return MUTE_TEXT


@time_log_decorator
async def send_keyboard(
    update: Update,
    context: CallbackContext,
    keyboard: InlineKeyboardMarkup,
    text=None,
    parse_mode=None,
):
    chat_id = update.effective_chat.id

    if text:
        # Mute a previous active window so only one active window can be in a chat
        await mute_last_active_keybpard(update, context)

        # Send a new start menu message
        # better through the bot, if menu was triggered by the callback
        # when a teacher enters for the fist time
        sent_message = await context.bot.send_message(
            chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode=parse_mode
        )

        # Store the message ID of the new start menu message
        await register_last_active_keyboard(context, sent_message.message_id)


async def register_last_active_keyboard(context: ContextTypes.DEFAULT_TYPE, message_id):
    context.chat_data["last_keyboard_message_id"] = message_id


async def mute_last_active_keybpard(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message_id = context.chat_data.get("last_keyboard_message_id")
    if message_id:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=get_mute_text_emoji(),
        )
        context.chat_data.pop("last_keyboard_message_id")


# Function to display or edit the start menu
async def show_or_edit_start_menu(update: Update, context: CallbackContext) -> int:
    keyboard = [[InlineKeyboardButton(BUTTON_TEXT, callback_data="start_conversation")]]
    keyboard = InlineKeyboardMarkup(keyboard)
    await send_keyboard(update, context, keyboard, text=KEYBOAD_TEXT)

    return SHOW_MENU


# Command handler function for /start
@time_log_decorator
async def start(update: Update, context: CallbackContext) -> int:
    return await show_or_edit_start_menu(update, context)


# Callback query handler function to start the conversation
@time_log_decorator
async def start_conversation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=INPUT_TEXT_MESSAGE)
    return INPUT_TEXT


# Message handler function for the conversation
@time_log_decorator
async def receive_text(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    await update.message.reply_text(BUTTON_REPLY_MESSAGE.format(user_input))
    # Show the menu again (or edit if it already exists)
    return await show_or_edit_start_menu(update, context)


@time_log_decorator
async def cancel(update: Update, context: CallbackContext) -> int:
    await show_or_edit_start_menu(update, context)
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TG_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INPUT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text)],
            SHOW_MENU: [
                CallbackQueryHandler(start_conversation, pattern="^start_conversation$")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", start),
        ],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
