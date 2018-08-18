import asyncio
import curses
from ui.ui_utils import calc_mutations
import ui.ui as ui
from utils.log import log
from utils.globals import gc
from utils.settings import settings

async def on_incoming_message(msg):

    # TODO: make sure it isn't a private message

    # find the guild/channel it belongs to and add it
    doBreak = False
    for guild_log in gc.guild_log_tree:
        if guild_log.guild == msg.guild:
            for channel_log in guild_log.logs:
                if channel_log.channel == msg.channel:
                    if channel_log.channel not in gc.channels_entered:
                        await gc.client.init_channel(channel_log.channel)
                    else:
                        channel_log.append(calc_mutations(msg))
                        gc.ui.channel_log_offset += 1
                    if channel_log.channel is not gc.client.current_channel:
                        if msg.guild.me.mention in msg.content:
                            channel_log.mentioned_in = True
                        else:
                            channel_log.unread = True
                    if msg.guild.me.mention in msg.content and \
                            "beep_mentions" in settings and \
                            settings["beep_mentions"]:
                        curses.beep()
                        log("Beep!")
                    doBreak = True
                    break
        if doBreak:
            break

    # redraw the screen if new msg is in current guild
    if msg.channel is gc.client.current_channel:
        ui.draw_screen()
