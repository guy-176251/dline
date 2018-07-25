import asyncio
import curses
from ui.ui_utils import calc_mutations
from utils.log import log
from utils.globals import gc
from utils.settings import settings

async def on_incoming_message(msg):

    # TODO: make sure it isn't a private message

    # find the server/channel it belongs to and add it
    doBreak = False
    for server_log in gc.server_log_tree:
        if server_log.server == msg.server:
            for channel_log in server_log.logs:
                if channel_log.channel == msg.channel:
                    if channel_log.channel not in gc.channels_entered:
                        await gc.client.init_channel(channel_log.channel)
                    else:
                        channel_log.append(calc_mutations(msg))
                        gc.ui.channel_log_offset += 1
                    if channel_log.channel is not gc.client.current_channel:
                        if msg.server.me.mention in msg.content:
                            channel_log.mentioned_in = True
                        else:
                            channel_log.unread = True
                    if msg.server.me.mention in msg.content and \
                            "beep_mentions" in settings and \
                            settings["beep_mentions"]:
                        curses.beep()
                        log("Beep!")
                    doBreak = True
                    break
        if doBreak:
            break

    # redraw the screen if new msg is in current server
    if msg.server is gc.client.current_server:
        gc.ui.doUpdate = True
