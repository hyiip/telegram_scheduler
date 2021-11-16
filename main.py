from telegram.ext import Dispatcher, CommandHandler
from telegram import Update, Bot
import os
from dotenv import load_dotenv
from handler.BotHandler import start,schedule
load_dotenv()
TelegramBotToken = os.environ['TGTOKEN']
bot = Bot(token=TelegramBotToken)
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("schedule", schedule))

def gcf_handler(request):
    if request.method == "POST":
        try:
            dispatcher.process_update(
                Update.de_json(request.get_json(force=True), bot)
            )
        except Exception as e:
            print(e)
            return (str(e), 500)
    return ("OK", 200)