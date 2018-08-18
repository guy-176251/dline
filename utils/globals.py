import time
import sys
import asyncio
import threading
from blessings import Terminal
from utils.settings import settings
from utils.log import log
from utils.threads import UiThread

NO_SETTINGS=False
try:
    if sys.argv[1] == "--store-token" or sys.argv[1] == "--token":
        NO_SETTINGS=True
except IndexError:
    pass

class GlobalsContainer:
    def __init__(self):
        self.term = Terminal()
        self.client = None
        self.ui_thread = UiThread(self)
        self.typing_handler_thread = None
        self.key_input_thread = None
        self.exit_thread = None
        self.ui = self.ui_thread.ui
        self.guild_log_tree = []
        self.channels_entered = []
        self.typingBeingHandled = False
        self.doExit = False
        self.tasksExited = 0

    def initClient(self):
        from client.client import Client
        if NO_SETTINGS:
            messages=100
        else:
            messages=settings["max_messages"]
        self.client = Client(max_messages=messages)

gc = GlobalsContainer()

# kills the program and all its elements gracefully
def kill():
    # attempt to cleanly close our loops
    threads = (gc.ui_thread, gc.typing_handler_thread, gc.key_input_thread)
    gc.doExit = True
    for tid,thread in enumerate(threads):
        while thread.is_alive():
            time.sleep(0.1)
    loop = gc.client.loop
    loop.create_task(gc.client.close())
    sys.exit(0) #return us to main()

# returns a "Channel" object from the given string
async def string2channel(channel):
    for srv in gc.client.guilds:
        if srv.name == channel.guild.name:
            for chan in srv.channels:
                if chan.name == channel:
                    return chan

# returns a "Channellog" object from the given string
async def get_channel_log(channel):
    for srvlog in gc.guild_log_tree:
        if srvlog.name.lower() == channel.guild.name.lower():
            for chanlog in srvlog.logs:
                if chanlog.name.lower() == channel.name.lower():
                    return chanlog
