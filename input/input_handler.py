import asyncio
import curses
import logging
from utils.log import log
import discord
from input.kbhit import KBHit
import ui.ui as ui
from utils.globals import gc, kill
from utils.settings import settings
from commands.text_emoticons import check_emoticons
from commands.sendfile import send_file
from commands.channel_jump import channel_jump
from input.messageEdit import MessageEdit

def init_channel_messageEdit(channel):
    gc.ui.messageEdit[channel.id] = MessageEdit(gc.ui.max_x, channel.name)

async def key_input():
    # if the next two aren't here, input does not work
    curses.cbreak()
    curses.noecho()
    editBar = gc.ui.editBar
    try:
        gc.ui.edit = gc.ui.messageEdit[gc.client.current_channel.id]
    except:
        init_channel_messageEdit(gc.client.current_channel)
        gc.ui.edit = gc.ui.messageEdit[gc.client.current_channel.id]
    await ui.draw_bottom_bar()
    while not gc.doExit:
        prompt = gc.client.prompt
        ch = editBar.getch()
        if ch == -1 or not gc.ui.displayPanel.hidden():
            await asyncio.sleep(0.01)
            continue
        if chr(ch) != '\n':
            gc.typingBeingHandled = True
        # prevents crashes when enter is hit and input buf is empty
        if chr(ch) == '\n' and not gc.ui.edit.inputBuffer:
            continue
        if ch == curses.KEY_PPAGE:
            gc.ui.channel_log_offset -= settings["scroll_lines"]
            gc.ui.doUpdate = True
            while gc.ui.doUpdate:
                await asyncio.sleep(0.01)
            continue
        elif ch == curses.KEY_NPAGE:
            gc.ui.channel_log_offset += settings["scroll_lines"]
            gc.ui.doUpdate = True
            while gc.ui.doUpdate:
                await asyncio.sleep(0.01)
            continue
        elif ch == curses.KEY_RESIZE:
            gc.ui.resize()
            gc.ui.doUpdate = True
            while gc.ui.doUpdate:
                await asyncio.sleep(0.01)
            continue
        await ui.draw_bottom_bar()
        ret = gc.ui.edit.addKey(ch)
        if ret is not None:
            await input_handler(ret)
            gc.ui.edit.reset()
        await ui.draw_bottom_bar()
    log("key_input finished")
    gc.tasksExited += 1

async def typing_handler():
    if not settings["send_is_typing"]: return

    while not gc.doExit:
        if gc.typingBeingHandled:
            await gc.client.send_typing(gc.client.current_channel)
            for second in range(50):
                if gc.doExit:
                    break
                await asyncio.sleep(0.1)
            gc.typingBeingHandled = False
            if gc.doExit:
                break
        await asyncio.sleep(0.1)
    log("typing_handler finished")
    gc.tasksExited += 1

async def input_handler(text):
    # Must be a command
    if text.startswith(settings["prefix"]):
        text = text[1:]
        arg = None
        if ' ' in text:
            command,arg = text.split(" ", 1)
        elif not text:
            return
        else:
            command = text
            arg = None
        await parseCommand(command, arg)
    # Must be text
    else:
        # Emoji
        if text.count(':')%2 == 0:
            text = await parseEmoji(text)
        if '@' in text:
            sections = text.lower().strip().split()
            secs_copy = []
            for sect in sections:
                if '@' in sect:
                    for member in gc.client.current_server.members:
                        if member is not gc.client.current_server.me and \
                                sect[1:] in member.display_name.lower():
                            sect = "<@!" + member.id + ">"
                sects_copy.append(sect)
            text = " ".join(sects_copy)
        sent = False
        for i in range(0,3):
            try:
                await gc.client.send_message(gc.client.current_channel, text)
                sent = True
                break
            except:
                await asyncio.sleep(3)

async def parseCommand(command, arg=None):
    if command in ("server", 's'):
        prev_server = gc.client.current_server
        gc.client.current_server = arg
        if gc.client.current_server is prev_server:
            return
        log("changed server")
        gc.ui.channel_log_offset = -1
        gc.ui.doUpdate = True
        while gc.ui.doUpdate:
            await asyncio.sleep(0.01)
    elif command in ("channel", 'c'):
        gc.client.current_channel = arg
    elif command == "nick":
        try:
            await gc.client.change_nickname(gc.client.current_server.me, arg)
        except:
            pass
    elif command == "game":
        await gc.client.set_game(arg)
    elif command == "file":
        await send_file(gc.client, arg)
    elif command == "status":
        status = arg.lower()
        if status in ("away", "afk"):
            status = "idle"
        elif "disturb" in status:
            status = "dnd"

        if status in ("online", "offline", "idle", "dnd"):
            gc.client.status = status

    if arg is None:
        if command in ("refresh", "update"):
            gc.ui.doUpdate = True
            while gc.ui.doUpdate:
                await asyncio.sleep(0.01)
            log("Manual update done", logging.info)
        elif command in ("quit", "exit"):
            try: gc.tasks.append(asyncio.get_event_loop().create_task(kill()))
            except SystemExit: pass
        elif command in ("help", 'h'): await ui.draw_help()
        elif command in ("servers", "servs"): await ui.draw_serverlist()
        elif command in ("channels", "chans"): await ui.draw_channellist()
        elif command == "emojis": await ui.draw_emojilist()
        elif command in ("users", "members"): await ui.draw_userlist()
        elif command[0] == 'c':
            try:
                if command[1].isdigit():
                    await channel_jump(command)
            except IndexError:
                pass
        await check_emoticons(gc.client, command)

async def parseEmoji(text):
    if settings["has_nitro"]:
        for emoji in gc.client.get_all_emojis():
            short_name = ':' + emoji.name + ':'
            if short_name in text:
                full_name = "<:{}:{}>".format(emoji.name, emoji.id)
                text = text.replace(short_name, full_name)
    elif gc.client.current_server.emojis is not None and \
            len(gc.client.current_server.emojis) > 0:
        for emoji in gc.client.current_server.emojis:
            short_name = ':' + emoji.name + ':'
            if short_name in text:
                full_name = "<:{}:{}>".format(emoji.name, emoji.id)
                text = text.replace(short_name, full_name)

    return text
