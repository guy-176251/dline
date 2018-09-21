import os
import sys
import logging
from datetime import datetime

logging_enabled = False
message_logging_enabled = False

class ErrorWriter:
    def write(self, message):
        if message != '\n':
            logging.error(message)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        logging.error("", exc_info(exc_type, exc_value, exc_traceback))

def startLogging(do_msg_log=False):
    global logging_enabled
    logging_enabled = True
    if do_msg_log:
        global message_logging_enabled
        message_logging_enabled = True
    configPath = os.getenv("HOME") + "/.config/dline"
    if os.path.exists(configPath):
        logging.basicConfig(filename=configPath + "/debug.log", filemode='w',
                level=logging.INFO)
    else:
        logging.basicConfig(filename="debug.log", filemode='w', level=logging.INFO)
    # needed to catch stderr messages
    ew = ErrorWriter()
    sys.stderr = ew
    sys.excepthook = ew.exception_hook

def log(msg, func=logging.info):
    if not logging_enabled:
        return
    func(msg)

def msglog(message):
    if not message_logging_enabled:
        return
    guild_name = message.guild.name.replace('/','_')
    channel_name = message.channel.name
    author_name = message.author.display_name
    content = message.clean_content
    date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    dirpath = "~/.config/dline/logs/" + guild_name

    os.makedirs(os.path.expanduser(dirpath), exist_ok=True)
    with open("{}/{}.log".format(os.path.expanduser(dirpath), channel_name), 'a') as f:
        f.write("{} {}: {}\n".format(date_time, author_name, content))
