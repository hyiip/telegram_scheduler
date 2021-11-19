from telegram.ext import Dispatcher, CommandHandler
from telegram import Update, Bot
import os
import json
from dotenv import load_dotenv
from handler.BotHandler import start, schedule_from_second, schedule_from_time
load_dotenv()
TelegramBotToken = os.environ['TGTOKEN']
bot = Bot(token=TelegramBotToken)
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("schedule_second", schedule_from_second))
dispatcher.add_handler(CommandHandler("schedule_time", schedule_from_time))

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

def task_handler(request):
    if request.method == "POST":
        body = json.loads(request.data.decode('utf-8'))
        msg = body.get("msg_text","")
        chat_id = body["chat_id"]
        bot.send_message(text=msg, chat_id=chat_id)
    return ("OK", 200)
