from telegram.ext import CommandHandler

# My commands live here
COMMAND_HANDLERS = {}


# A decorator that registers a command
def command_handler(func):
    """
    A decorator to register a function as a command handler for a specific flag.
    """

    COMMAND_HANDLERS[func.__name__] = CommandHandler(func.__name__, func)

    return func


# Function to add all registered handlers to the application
def add_command_handlers(application):
    for handler in COMMAND_HANDLERS.values():
        application.add_handler(handler)
