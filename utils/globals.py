from blessings import Terminal
from utils.settings import settings
from utils.log import log
from utils.threads import UiThread
import sys

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
        self.ui = self.ui_thread.ui
        self.init_channel_lock = False
        self.server_log_tree = []
        self.channels_entered = []
        self.typingBeingHandled = False
        self.doExit = False
        self.tasks = []
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
async def kill():
    # attempt to cleanly close our loops
    import asyncio
    from os import system
    gc.doExit = True
    while gc.tasksExited < 3:
        await asyncio.sleep(0.01)
    sys.exit(0) #return us to main()

# returns a "Channel" object from the given string
async def string2channel(channel):
    for srv in gc.client.servers:
        if srv.name == channel.server.name:
            for chan in srv.channels:
                if chan.name == channel:
                    return chan

# returns a "Channellog" object from the given string
async def get_channel_log(channel):
    for srvlog in gc.server_log_tree:
        if srvlog.name.lower() == channel.server.name.lower():
            for chanlog in srvlog.logs:
                if chanlog.name.lower() == channel.name.lower():
                    return chanlog
