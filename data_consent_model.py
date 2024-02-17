from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from datetime import datetime

from callback_handlers import callback_handler
from command_handlers import command_handler

import handlers


# Constants
PARSE_MODE = "MarkdownV2"
DATA_POLICY = "*Продовжуючи\, ви надаєте згоду на збір та обробку деяких ваших персональних даних\.*"
CONFIRM_TEXT = "Ви надали свою згоду на збір та обробку даних\, *дякую*\!"
NOT_CONFIRM_TEXT = "🙊🙉🙈"
CONFIRM_BUTTON = "Продовжити / Continue"
EXIT_BUTTON = "Вийти / Exit"

# States
DATA_CONSENT = 0 # reserved state


@command_handler
async def start(update: Update, context: CallbackContext):
    if "data_policy" not in context.bot_data:
        context.bot_data["data_policy"] = DATA_POLICY

    if "data_consent" not in context.user_data:
        keyboard = [
            [InlineKeyboardButton(CONFIRM_BUTTON, callback_data="data_consent")],
            [InlineKeyboardButton(EXIT_BUTTON, callback_data="not_data_consent")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return await update.message.reply_text(
            text=DATA_POLICY, reply_markup=reply_markup, parse_mode=PARSE_MODE
        )


def get_user_full_tg_info(user) -> dict:
    # Gather user info from telegram user object
    user_info = {
        "is_bot": user.is_bot,
        "signed_at": datetime.now(),
        "tg_username": f"@{user.username}" if user.username else "None",
        "tg_first_name": f"{user.first_name}" if user.first_name else "None",
        "tg_last_name": f"{user.last_name}" if user.last_name else "None",
        "tg_language": f"{user.language_code}" if user.language_code else "None",
    }
    return user_info


@callback_handler
async def data_consent(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    context.user_data["data_consent"] = True
    context.user_data["info"] = get_user_full_tg_info(update.effective_user)
    await query.edit_message_text(CONFIRM_TEXT, parse_mode=PARSE_MODE)
    return await handlers.start(update, context)


@callback_handler
async def not_data_consent(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(NOT_CONFIRM_TEXT, parse_mode=PARSE_MODE)
