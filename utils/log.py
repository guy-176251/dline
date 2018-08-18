import os
import logging
from datetime import datetime
from utils.settings import settings

def startLogging():
    configPath = os.getenv("HOME") + "/.config/Discline"
    if os.path.exists(configPath):
        logging.basicConfig(filename=configPath + "/discline.log", filemode='w',
                level=logging.INFO)
    else:
        logging.basicConfig(filename="discline.log", filemode='w', level=logging.INFO)

def log(msg, func=logging.info):
    if settings["debug"]:
        func(msg)

def msglog(message):
    try:
        if not settings['message_log']:
            return
    except:
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
