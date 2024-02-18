from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from callback_handlers import callback_handler

from datetime import datetime
import json

from button_dialog_model import send_keyboard
import settings

from mylogging import logger, time_log_decorator


CLEAN_DATA_FILE_PATH = "CleanWordsAlphabetOrder-bl.json"
PROCESSED_DATA_FILE_PATH = "HumanProcessedWordsAlphabetOrder-bl.json"

QUESTIONS_DONE_MESSAGE = "Ура, всі завдання виконано! Дякую."
ADMIN_DONE_MESSAGE = "Все!"
IS_SENT = False

NEXT_BUTTON = "Далі"
NEXT_MESSAGE = "Продовжити?"


async def error(update: Update, context: CallbackContext) -> None:
    # For callback queries
    if update.callback_query:
        await update.callback_query.answer("A callback error occurred", show_alert=True)
    # For regular messages
    elif update.message:
        await update.message.reply_text("A message error occurred")
    else:
        logger.error(f"Update {update} caused error {context.error}")


@time_log_decorator
def get_user_full_tg_info(user) -> dict:
    # Gather user info from telegram user object
    user_info = {
        "added_on": datetime.now(),
        "tg_username": f"@{user.username}" if user.username else "None",
        "tg_first_name": f"{user.first_name}" if user.first_name else "None",
        "tg_last_name": f"{user.last_name}" if user.last_name else "None",
        "is_bot": user.is_bot,
    }
    return user_info


@time_log_decorator
async def start(update: Update, context: CallbackContext):
    current_questions = context.bot_data.get("current_questions")
    if current_questions is None:  # first user starts
        prepare_questions(context)
    return await continue_quiz(update, context)


@time_log_decorator
def prepare_questions(context):
    with open(CLEAN_DATA_FILE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    context.bot_data["current_name"] = data["name"]
    context.bot_data["current_questions"] = data["instances"]
    context.bot_data["current_answers"] = []


@time_log_decorator
def get_options_from_question(question: str):
    question = question.get("question")
    question = question.replace("?", "")

    if question.startswith("Серед"):
        question = question.replace("'", "")
        question = question.replace("Серед ", "")
        options, question = question.split(",")
        question = question.strip().capitalize()
        op_list = (
            [w.strip() for w in options.split(" і ")]
            if " і " in options
            else [w.strip() for w in options.split(" та ")]
        )
    else:
        question = question.replace('"', "")
        question, options = question.split(":")
        op_list = [w.strip() for w in options.split(" чи ")]
    return question, op_list


@time_log_decorator
@callback_handler
async def next(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        await query.answer()

    current_questions = context.bot_data.get("current_questions")
    if not current_questions:
        chat_id = update.effective_chat.id
        message_id = context.chat_data.get("last_keyboard_message_id")
        await save_answers(context)
        if query:
            return await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=QUESTIONS_DONE_MESSAGE,
                reply_markup=keyboard,
            )
        return await update.message.reply_text(QUESTIONS_DONE_MESSAGE)

    raw_question = context.bot_data["current_questions"].pop()
    context.user_data["current_question"] = raw_question

    question, options = get_options_from_question(raw_question)
    question += '?'
    buttons = [
        [
            InlineKeyboardButton(
                option,
                callback_data=f"click_item_{option}",
            )
        ]
        for option in options
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    return await send_keyboard(update, context, keyboard, text=question)


@time_log_decorator
@callback_handler
async def click_item(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("click_item"):
        data = data.replace("click_item_", "")

    current_question = context.user_data.pop("current_question")
    current_question["humanAnswer"] = data.strip()
    context.bot_data["current_answers"].append(current_question)

    if not context.user_data.get("logs"):
        context.user_data["logs"] = []
    context.user_data["logs"].append(
        {"time": datetime.now(), "answer": current_question}
    )

    return await continue_quiz(update, context)


@time_log_decorator
@callback_handler
async def continue_quiz(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(
                NEXT_BUTTON,
                callback_data="next",
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    return await send_keyboard(update, context, keyboard, text=NEXT_MESSAGE)


@time_log_decorator
async def save_answers(context):
    global IS_SENT

    if not IS_SENT:
        questions_data = {
            "name": context.bot_data.get("current_name", "Unknown"),
            "instances": context.bot_data.get("current_answers", []),
        }

        # Save to file
        with open(PROCESSED_DATA_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(questions_data, file, ensure_ascii=False, indent=4)

        for admin_id in settings.ADMIN_GROUP:
            try:
                with open(PROCESSED_DATA_FILE_PATH, "rb") as file:
                    await context.bot.send_document(
                        chat_id=admin_id, document=file, caption=ADMIN_DONE_MESSAGE
                    )
                    IS_SENT = True

            except Exception as e:
                logger.error(
                    f"Failed to send notification to admin {admin_id}: {e}"
                )
