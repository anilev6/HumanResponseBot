from telegram.ext import CallbackQueryHandler

# A dictionary to hold callback handlers, mapping flags to functions
CALLBACK_HANDLERS = {}


# A decorator that connects the callback data with the function name
def callback_handler(func):
    """
    A decorator to register a function as a callback handler for a specific flag.
    """

    # Register the function as a handler
    CALLBACK_HANDLERS[func.__name__] = CallbackQueryHandler(
        func, pattern=f"^{func.__name__}.*"
    )

    return func


# Function to add all registered callbacks to the application
def add_callback_handlers(application):
    for handler in CALLBACK_HANDLERS.values():
        application.add_handler(handler)
