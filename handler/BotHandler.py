from telegram import Update
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Bot started")
    print("start success")

def schedule(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    try:
        second = context.args[0]
        raw = context.args[1:]
        msg_text = " ".join(raw)
        context.bot.send_message(chat_id=chat_id, text="Message schedule in {} second: {}".format(second, msg_text))
        print("schedule success")
    except:
        context.bot.send_message(chat_id=chat_id, text="Usage: /schehule second message\n Eg: /schedule 1 test message")
        print("fail")
        