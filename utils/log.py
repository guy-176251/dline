import os
import logging
from datetime import datetime

logging_enabled = False
message_logging_enabled = False

def startLogging(do_msg_log=False):
    global logging_enabled
    logging_enabled = True
    if do_msg_log:
        global message_logging_enabled
        message_logging_enabled = True
    configPath = os.getenv("HOME") + "/.config/Discline"
    if os.path.exists(configPath):
        logging.basicConfig(filename=configPath + "/discline.log", filemode='w',
                level=logging.INFO)
    else:
        logging.basicConfig(filename="discline.log", filemode='w', level=logging.INFO)

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
    dirpath = "~/.config/Discline/logs/" + guild_name

    os.makedirs(os.path.expanduser(dirpath), exist_ok=True)
    with open("{}/{}.log".format(os.path.expanduser(dirpath), channel_name), 'a') as f:
        f.write("{} {}: {}\n".format(date_time, author_name, content))
