import time
import sys
from blessings import Terminal

class Found(Exception):
    pass
class NoChannelsFoundException(Exception):
    pass
class OutdatedConfigException(Exception):
    pass

class GlobalsContainer:
    def __init__(self):
        from dline.utils.threads import UiThread
        self.settings = {}
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
        from dline.client.client import Client
        try:
            messages=self.settings["max_messages"]
        except:
            messages=100
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
