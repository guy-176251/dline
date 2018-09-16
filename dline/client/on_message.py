import curses
from discord import TextChannel, DMChannel, GroupChannel
from dline.ui.ui_utils import calc_mutations
import dline.ui.ui as ui
from dline.utils.log import log
from dline.utils.globals import gc

async def process_message(msg, channel_log):
    if channel_log.channel not in gc.channels_entered:
        await gc.client.init_channel(channel_log.channel)
    else:
        channel_log.append(calc_mutations(msg))
        gc.ui.channel_log_offset += 1
    if msg.guild is not None and \
            channel_log.channel is not gc.client.current_channel:
        if msg.guild.me.mention in msg.content:
            channel_log.mentioned_in = True
        else:
            channel_log.unread = True
    if msg.guild is not None and \
            msg.guild.me.mention in msg.content and \
            "beep_mentions" in gc.settings and \
            gc.settings["beep_mentions"]:
        curses.beep()
        log("Beep!")
    if channel_log is gc.client.current_channel_log:
        ui.draw_screen()

async def on_incoming_message(msg):
    # find the guild/channel it belongs to and add it
    if isinstance(msg.channel, DMChannel) or \
            isinstance(msg.channel, GroupChannel):
        guild_log = gc.guild_log_tree[0]
        for channel_log in guild_log.logs:
            users = []
            for user in channel_log.channel.members:
                users.append(user)
            if msg.author in users and \
                    msg.channel is channel_log.channel._channel:
                await process_message(msg, channel_log)
                return
        log("Could not find matching channel log")
    elif isinstance(msg.channel, TextChannel):
        doBreak = False
        for guild_log in gc.guild_log_tree:
            if guild_log.guild == msg.guild:
                for channel_log in guild_log.logs:
                    if channel_log.channel == msg.channel:
                        await process_message(msg, channel_log)
                        doBreak = True
                        break
            if doBreak:
                break
