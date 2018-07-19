#!/usr/bin/python3
# ------------------------------------------------------- #
#                                                         #
# Discline                                                #
#                                                         #
# http://github.com/NatTupper/Discline                    #
#                                                         #
# Licensed under GNU GPLv3                                #
#                                                         #
# ------------------------------------------------------- #

import sys
import asyncio
import curses
import os
import threading
from discord import ChannelType, MessageType
from input.input_handler import key_input, typing_handler
from ui.ui import draw_screen, start_ui, draw_help
from utils.globals import *
from utils.settings import copy_skeleton, settings
from utils.updates import check_for_updates
from utils.token_utils import get_token, store_token
from utils.log import log, startLogging, msglog
from client.serverlog import ServerLog
from client.channellog import ChannelLog
from client.on_message import on_incoming_message
from client.client import Client

init_complete = False

# Set terminal X11 window title
print('\33]0;Discline\a', end='', flush=True)

gc.initClient()

@gc.client.event
async def on_ready():
    # these values are set in settings.yaml
    if settings["default_prompt"] is not None:
        gc.client.prompt = settings["default_prompt"].lower()
    else:
        gc.client.prompt = '~'

    if settings["default_game"] is not None:
        await gc.client.set_game(settings["default_game"])

    for server in gc.client.servers:
        # Null check to check server availability
        if server is None:
            continue
        serv_logs = []
        for channel in server.channels:
            # Null checks to test for bugged out channels
            if channel is None or channel.type is None:
                continue
            # Null checks for bugged out members
            if server.me is None or server.me.id is None \
                    or channel.permissions_for(server.me) is None:
                continue
            if channel.type == ChannelType.text:
                    if channel.permissions_for(server.me).read_messages:
                        try: # try/except in order to 'continue' out of multiple for loops
                            for serv_key in settings["channel_ignore_list"]:
                                if serv_key["server_name"].lower() == server.name.lower():
                                    for name in serv_key["ignores"]:
                                        if channel.name.lower() == name.lower():
                                            raise Found
                            serv_logs.append(ChannelLog(channel, []))
                        except:
                            continue

        # add the channellog to the tree
        gc.server_log_tree.append(ServerLog(server, serv_logs))

    if settings["default_server"] is not None:
        gc.client.set_current_server(settings["default_server"])
        if gc.client.current_server is None:
            print("ERROR: default_server not found!")
            raise KeyboardInterrupt
            return
        if settings["default_channel"] is not None:
            gc.client.current_channel = settings["default_channel"].lower()
            gc.client.prompt = settings["default_channel"].lower()

    # start our own coroutines
    gc.ui_thread.start()
    while not gc.ui.isInitialized:
        await asyncio.sleep(0.1)
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(draw_screen())
        loop.create_task(key_input())
        loop.create_task(typing_handler())
    except SystemExit: pass
    except KeyboardInterrupt: pass

    global init_complete
    init_complete = True

# called whenever the client receives a message (from anywhere)
@gc.client.event
async def on_message(message):
    await gc.client.wait_until_ready()
    if init_complete:
        msglog(message)
        await on_incoming_message(message)

@gc.client.event
async def on_message_edit(msg_old, msg_new):
    await gc.client.wait_until_ready()
    if msg_old.clean_content == msg_new.clean_content:
        return
    clog = gc.client.current_channel
    if clog is None:
        return
    ft = gc.ui.views[clog.id].formattedText
    msg_new.content = msg_new.content + " **(edited)**"
    idx = 0
    while True:
        if len(ft.messages) >= idx:
            break
        if ft.messages[idx].id == msg_old.id:
            ft.messages[idx].content = msg_new.content
            break
        idx += 1
    ft.refresh()

    if init_complete:
        gc.ui.doUpdate = True

@gc.client.event
async def on_message_delete(msg):
    log("Attempting to delete")
    await gc.client.wait_until_ready()
    # TODO: PM's have 'None' as a server -- fix this later
    if msg.server is None: return

    try:
        for serverlog in gc.server_log_tree:
            if serverlog.server == msg.server:
                for channellog in serverlog.logs:
                    if channellog.channel == msg.channel:
                        ft = gc.ui.views[channellog.channel.id].formattedText
                        channellog.logs.remove(msg)
                        ft.messages.remove(msg)
                        ft.refresh()
                        log("Deleted, updating")
                        gc.ui.doUpdate = True
                        return
    except:
        # if the message cannot be found, an exception will be raised
        # this could be #1: if the message was already deleted,
        # (happens when multiple calls get excecuted within the same time)
        # or the user was banned, (in which case all their msgs disappear)
        pass
    log("Could not delete message: {}".format(msg.clean_content))

def runTest(test):
    # input_handler.py
    if test == "input":
        inputTestLauncher()
    elif test == "formatting":
        formattingTestLauncher()
    elif test == "scrolling":
        scrollingTestLauncher()
    elif test == "sendrecv":
        sendrecvTestLauncher()

async def runSimpleHelp():
    await start_ui()
    await draw_help(terminateAfter=True)

def terminate_curses():
    curses.nocbreak()
    gc.ui.screen.keypad(False)
    curses.echo()
    curses.endwin()

def main():
    # start the client coroutine
    if settings and settings["debug"]:
        startLogging()
    token = None
    try:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            try:
                asyncio.get_event_loop().run_until_complete(runSimpleHelp())
            except SystemExit:
                pass
            terminate_curses()
            quit()
        elif sys.argv[1] == "--token" or sys.argv[1] == "--store-token":
            store_token()
            quit()
        elif len(sys.argv) == 3 and sys.argv[1] == "--token-path":
            try:
                with open(sys.argv[2]) as f:
                    token = f.read()
            except:
                print("Error: Cannot read token from path")
                quit()
        elif sys.argv[1] == "--skeleton" or sys.argv[1] == "--copy-skeleton":
            # -- now handled in utils.settings.py --- #
            pass
        elif sys.argv[1] == "--config":
            # -- now handled in utils.settings.py --- #
            pass
        else:
            print(gc.term.red("Error: Unknown command."))
            print(gc.term.yellow("See --help for options."))
            quit()
    except IndexError:
        pass

    check_for_updates()
    if token is None:
        token = get_token()

    print(gc.term.yellow("Starting..."))

    # start the client
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(gc.client.start(token, bot=False))
    except:
        pass

    # stop the client and close the event loop
    try:
        gc.client.close()
        loop.close()
    except:
        pass

    if gc.ui.isInitialized:
        terminate_curses()

if __name__ == "__main__": main()
