from mongopersistence import MongoPersistence
from telegram.ext import ApplicationBuilder

from settings import MONGO_URL, TG_BOT_TOKEN


# -------------------------------------------TELEGRAM BOT DB------------------------------
persistence = MongoPersistence(
    mongo_url=MONGO_URL,
    db_name="human-response-language-quiz-bot-database",
    name_col_user_data="user-data-collection",
    name_col_chat_data="chat-data-collection",
    name_col_bot_data="bot-data-collection",
    create_col_if_not_exist=True,
    load_on_flush=False,
    update_interval=60,
)

# --------------------------------------------TELEGRAM APP---------------------------------
application = (
    ApplicationBuilder()
    .token(TG_BOT_TOKEN)
    .persistence(persistence)
    .build()
)
