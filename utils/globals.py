from sys import exit
from blessings import Terminal
from utils.settings import settings
from ui.ui import CursesUI
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
        self.ui = CursesUI()
        self.server_log_tree = []
        self.channels_entered = []
        self.typingBeingHandled = False

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
    import asyncio
    try: gc.client.close()
    except: pass
    try: asyncio.get_event_loop().close()
    except: pass
    try:# since we're exiting, we can be nice and try to clear the screen
        from os import system
        system("clear")
    except: pass
    exit()

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
