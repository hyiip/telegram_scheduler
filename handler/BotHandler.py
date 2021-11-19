from telegram import Update
from telegram.ext import CallbackContext
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime
import os
import json
from dateutil import parser, tz
from dotenv import load_dotenv
load_dotenv()
project = os.environ["task_project"]
queue = os.environ["task_queue"]
location = os.environ["task_location"]
url = os.environ["task_url"]
audience = url
service_account_email = os.environ["gcp_service_account_email"]
client = tasks_v2.CloudTasksClient()
parent = client.queue_path(project, location, queue)

def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Bot started")
    print("start success")

def schedule_from_second(update: Update, context: CallbackContext):
    task = {
        "http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,  # The full url path that the task will be sent to.
            "oidc_token": {"service_account_email": service_account_email, "audience": audience},
        }
    }
    chat_id = update.message.chat_id
    try:
        raw = context.args[1:]
        if not raw:
            raise IndexError("list index out of range")
        msg_text = " ".join(raw)
        payload = {
            "msg_text": msg_text,
            "chat_id": chat_id
        }
        in_seconds = int(context.args[0])
        if in_seconds < 0:
            raise ValueError("seconds must not be negative")
        converted_payload = json.dumps(payload).encode()
        task["http_request"]["body"] = converted_payload
        task["http_request"]["headers"] = {"Content-type": "application/json"}
        current_time = datetime.datetime.utcnow()
        d = current_time + datetime.timedelta(seconds=in_seconds)
        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        # Add the timestamp to the tasks.
        task["schedule_time"] = timestamp
        current_time_string = str(current_time.timestamp()).replace(".", "-")
        task_name = "{chat_id}_{time}".format(chat_id=chat_id, time=current_time_string)
        task["name"] = client.task_path(project, location, queue, task_name)
        response = client.create_task(request={"parent": parent, "task": task})
        context.bot.send_message(chat_id=chat_id, text="Message schedule in {} seconds: {}".format(in_seconds, msg_text))
        print("schedule success")
    except (IndexError, ValueError) as e:
        context.bot.send_message(chat_id=chat_id, text="Usage: /schehule_second {positive second} {message}\n Eg: /schehule_second 1 test message")
        print("fail")

error_msg = '''Usage: /schedule_time {date}T{time} {message}
Some examples of time include:
11/19/2021-12:00+8
2021-11-19T12:00
2021-11-19/12:00+08:00
11-19T12:00:05
If timezone is not specified, UTC+8 will be assumed.
If the scheduled time is before current time, we will reschedule the message so that it will be sent on the next day.
Recommend to use T to separate date and time, but you can still use -, /, . Don't use space as a delimiter.'''
def schedule_from_time(update: Update, context: CallbackContext):
    task = {
        "http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,  # The full url path that the task will be sent to.
            "oidc_token": {"service_account_email": service_account_email, "audience": audience},
        }
    }
    chat_id = update.message.chat_id
    try:
        time = context.args[0]
        raw = context.args[1:]
        if not raw:
            raise IndexError("list index out of range")
        msg_text = " ".join(raw)
        payload = {
            "msg_text": msg_text,
            "chat_id": chat_id
        }
        current_time = datetime.datetime.now()
        dt = parser.parse(time, dayfirst = True,  default = current_time.replace(second=0, tzinfo=tz.gettz('Asia/Hong_Kong')) )
        while current_time.timestamp() - dt.timestamp() > 0:
            dt = dt + datetime.timedelta(days=1)
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(dt)
        converted_payload = json.dumps(payload).encode()
        task["http_request"]["body"] = converted_payload
        task["http_request"]["headers"] = {"Content-type": "application/json"}

        # Add the timestamp to the tasks.
        task["schedule_time"] = timestamp
        current_time_string = str(current_time.timestamp()).replace(".", "-")
        task_name = "{chat_id}_{time}".format(chat_id=chat_id, time=current_time_string)
        task["name"] = client.task_path(project, location, queue, task_name)
        response = client.create_task(request={"parent": parent, "task": task})
        context.bot.send_message(chat_id=chat_id, text="Message schedule on {}: {}".format(dt.replace(microsecond=0).isoformat(), msg_text))
        print("schedule success")
    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=chat_id, text=error_msg)
        print("fail")
        