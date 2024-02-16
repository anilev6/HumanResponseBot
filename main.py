import contextlib

from command_handlers import add_command_handlers
from callback_handlers import add_callback_handlers

from handlers import error
from app import application

def telegram_bot(application):

    add_command_handlers(application)
    add_callback_handlers(application)

    application.add_error_handler(error)

    with contextlib.suppress(KeyboardInterrupt): # Ignore exception when Ctrl-C is pressed
        application.run_polling(0.5)


if __name__ == "__main__":
    telegram_bot(application)
