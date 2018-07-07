import sys
import asyncio
import curses, curses.panel
from discord import ChannelType
from blessings import Terminal
from input.messageEdit import MessageEdit
from utils.log import log
from ui.ui_utils import get_role_color
from ui.userlist import UserList
from utils.quicksort import quick_sort_channels, quick_sort_channel_logs
from utils.settings import settings

hasItalic = False
if sys.version_info >= (3,7):
    hasItalic = True

line = 0

colorNames = {
        'black':curses.COLOR_BLACK+1,
        'red':curses.COLOR_RED+1,
        'green':curses.COLOR_GREEN+1,
        'yellow':curses.COLOR_YELLOW+1,
        'blue':curses.COLOR_BLUE+1,
        'magenta':curses.COLOR_MAGENTA+1,
        'cyan':curses.COLOR_CYAN+1,
        'white':curses.COLOR_WHITE+1
}

class CursesUI:
    def __init__(self):
        self.frameWins = []
        self.contentWins = []

        self.messageEdit = MessageEdit()
        self.views = {}
        self.isInitialized = False
        self.areLogsRead = False
        self.doUpdate = False
        self.channel_log_offset = -1
        # Windows
        self.topWin = None
        self.leftWin = None
        self.editWin = None
        self.chatWin = None
        self.chatWinWidth = 0
        self.userWin = None
        self.contentWins = []
        self.frameWin = None
        # Visibility
        self.separatorsVisible = True
        self.topWinVisible = True
        self.leftWinVisible = True
        self.userWinVisible = False

    def initScreen(self):
        self.screen.keypad(True)
        self.screen.clear()
        curses.cbreak()
        curses.noecho()
        self.colors = {}
        curses.use_default_colors()
        curses.curs_set(1)
        for i in range(1,9):
            curses.init_pair(i, i-1, -1)
        for key,value in colorNames.items():
            self.colors[key] = curses.color_pair(value)
        self.separatorsVisible = settings["show_separators"]
        try:
            self.topWinVisible = settings["show_top_win"]
            self.leftWinVisible = settings["show_left_win"]
        except:
            self.topWinVisible = settings["show_top_bar"]
            self.leftWinVisible = settings["show_left_bar"]
        try:
            self.userWinVisible = settings["show_user_win"]
        except:
            pass

    def resize(self):
        self.max_y, self.max_x = self.screen.getmaxyx()
        self.clearWins()
        if self.separatorsVisible:
            self.makeFrameWin(resize=True)
        if self.topWinVisible:
            self.makeTopWin(resize=True)
        self.makeBottomWin(resize=True)
        if self.leftWinVisible:
            self.makeLeftWin(resize=True)
        if self.userWinVisible:
            self.makeUserWin(resize=True)
        self.makeChatWin(resize=True)
        self.makeDisplay(resize=True)
        self.edit.maxWidth = self.max_x
        self.redrawFrames()

    def clearWins(self):
        self.frameWin.clear()
        for win in self.contentWins:
            win.clear()

    def makeFrameWin(self, resize=False):
        if resize:
            self.frameWin.resize(self.max_y,self.max_x)
            return
        self.frameWin = curses.newwin(self.max_y,self.max_x, 0,0)

    def makeTopWin(self, resize=False):
        if resize:
            self.topWin.resize(1,self.max_x)
            return
        content = curses.newwin(1,self.max_x, 0,0)
        self.topWin = content
        self.topWin.leaveok(True)

        self.contentWins.append(content)

    def makeBottomWin(self, resize=False):
        if resize:
            self.editWin.resize(1,self.max_x)
            self.editWin.mvwin(self.max_y-1,0)
            return
        content = curses.newwin(1,self.max_x, self.max_y-1,0)
        content.keypad(True)
        content.nodelay(True)
        self.editWin = content

        self.contentWins.append(content)

    def makeLeftWin(self, resize=False):
        # Win has 2 elements: frame and content pad
        width = self.leftWinWidth
        y_offset = 0
        if self.topWinVisible:
            y_offset = 2

        if resize:
            self.leftWin.resize(self.max_y-y_offset-2,width-1)
            return
        content = curses.newwin(self.max_y-y_offset-2,width-1, y_offset,0)
        self.leftWin = content
        self.leftWin.leaveok(True)

        self.contentWins.append(content)

    def makeUserWin(self, resize=False):
        width = self.userWinWidth
        y_offset = 0
        if self.topWinVisible:
            y_offset = 2

        if resize:
            self.userWin.resize(self.max_y-y_offset-2,width-1)
            return
        content = curses.newwin(self.max_y-y_offset-2,width-1, y_offset,self.max_x-width)
        self.userWin = content
        self.userWin.leaveok(True)

        self.contentWins.append(content)

    def makeChatWin(self, resize=False):
        x_offset = 0;width = self.max_x
        if self.leftWinVisible:
            x_offset = self.leftWinWidth+1
            width -= x_offset
        if self.userWinVisible:
            width -= self.userWinWidth+1
        y_offset = 0
        if self.topWinVisible:
            y_offset = 2

        if resize:
            self.chatWin.resize(self.max_y-y_offset-2,width)
            return
        content = curses.newwin(self.max_y-y_offset-2,width, y_offset,x_offset)
        self.chatWin = content
        self.chatWinWidth = width
        self.chatWin.leaveok(True)

    def makeDisplay(self, resize=False): #TODO: Make display separate view
        if resize:
            self.displayWin.resize(self.max_y,self.max_x)
            return
        self.displayWin = curses.newwin(self.max_y,self.max_x, 0,0)
        self.displayWin.keypad(True)
        self.displayWin.leaveok(True)
        self.displayWin.erase()
        self.displayPanel = curses.panel.new_panel(self.displayWin)
        self.displayPanel.hide()
        curses.panel.update_panels();self.screen.refresh()

    def refreshAll(self):
        for win in self.contentWins:
            win.noutrefresh()
        self.chatWin.noutrefresh()
        curses.doupdate()

    def run(self, screen):
        self.screen = screen
        self.initScreen()
        maxyx = self.screen.getmaxyx()
        self.max_y = maxyx[0]
        self.max_x = maxyx[1]
        self.waitUntilUserExit()

    def waitUntilUserExit(self):
        self.makeFrameWin()
        self.makeDisplay()
        try:
            self.leftWinWidth = int(self.max_x // settings["left_win_divider"])
            self.userWinWidth = int(self.max_x // settings["user_win_divider"])
        except:
            self.leftWinWidth = int(self.max_x // settings["left_bar_divider"])
            self.userWinWidth = int(self.max_x // settings["user_bar_divider"])
        if self.topWinVisible:
            self.makeTopWin()
        self.makeBottomWin()
        if self.leftWinVisible:
            self.makeLeftWin()
        if self.userWinVisible:
            self.makeUserWin()
        self.makeChatWin()
        self.redrawFrames()

        self.isInitialized = True

        self.refreshAll()

    def redrawFrames(self):
        # redraw top frame
        y_offset = 0
        if self.topWinVisible and self.separatorsVisible:
            y_offset = 1
            self.frameWin.hline(y_offset,0, curses.ACS_HLINE, self.max_x)
        # redraw bottom frame
        self.frameWin.hline(self.max_y-2,0, curses.ACS_HLINE, self.max_x)
        # redraw left frame
        if self.leftWinVisible and self.separatorsVisible:
            self.frameWin.vline(y_offset+1,self.leftWinWidth, curses.ACS_VLINE,
                    self.max_y-y_offset-3)
            self.frameWin.addch(y_offset,self.leftWinWidth, curses.ACS_TTEE)
            self.frameWin.addch(self.max_y-2,self.leftWinWidth, curses.ACS_BTEE)
        # redraw user frame
        if self.userWinVisible and self.separatorsVisible:
            self.frameWin.vline(y_offset+1,self.max_x-self.userWinWidth-1, curses.ACS_VLINE,
                    self.max_y-y_offset-3)
            self.frameWin.addch(y_offset,self.max_x-self.userWinWidth-1, curses.ACS_TTEE)
            self.frameWin.addch(self.max_y-2,self.max_x-self.userWinWidth-1, curses.ACS_BTEE)
        self.frameWin.refresh()

    def toggleDisplay(self):
        if self.displayPanel.hidden():
            self.displayPanel.show()
            curses.curs_set(0)
        else:
            self.displayPanel.hide()
            curses.curs_set(1)

        curses.panel.update_panels();self.screen.refresh()
        if self.displayPanel.hidden():
            self.redrawFrames()

from utils.globals import gc

async def start_ui():
    curses.wrapper(gc.ui.run)

async def draw_screen():
    gc.ui.doUpdate = True
    while not gc.doExit:
        if not gc.ui.isInitialized:
            await asyncio.sleep(0.01)
            continue
        if not gc.ui.doUpdate:
            await asyncio.sleep(0.01)
            continue
        log("Updating")
        if gc.ui.topWinVisible:
            await draw_top_win()
        if gc.ui.leftWinVisible:
            await draw_left_win()
        if gc.ui.userWinVisible:
            await draw_user_win()
        if gc.server_log_tree is not None:
            await draw_channel_log()
        await draw_edit_win()
        gc.ui.doUpdate = False
    log("draw_screen finished")
    gc.tasksExited += 1

async def draw_top_win():
    topWin = gc.ui.topWin
    width = topWin.getmaxyx()[1]
    color = gc.ui.colors[settings["server_display_color"]]

    serverName = gc.client.current_server.name

    topic = ""
    try:
        if gc.client.current_channel.topic is not None:
            topic = gc.client.current_channel.topic
        # if there is no channel topic, just print the channel name
        else:
            topic = gc.client.current_channel.name
    except: pass
    if len(topic) >= width//2:
        topic = topic[:width//2-3] + "..."
    topicOffset = width//2-len(topic)//2

    # sleep required to get accurate user count
    await asyncio.sleep(0.05)
    online = str(gc.client.online)
    online_text = "Users online: " + online
    onlineOffset = width-len(online_text)-1

    topWin.clear()

    topWin.addstr(0,0, "Server: ")
    topWin.addstr(serverName, color)

    topWin.addstr(0,topicOffset, topic)

    topWin.addstr(0,onlineOffset, "Users online: ", color)
    topWin.addstr(online)

    topWin.refresh()

async def set_display(string, attrs=0):
    display = gc.ui.displayWin
    gc.ui.toggleDisplay()
    display.addstr(string, attrs)
    display.refresh()
    while True:
        ch = display.getch()
        if ch == ord('q'):
            break
        asyncio.sleep(0.1)
    display.clear()
    gc.ui.toggleDisplay()

async def draw_left_win():
    leftWin = gc.ui.leftWin
    left_win_width = leftWin.getmaxyx()[1]

    if gc.ui.separatorsVisible:
        length = 0
        length = gc.term.height - settings["margin"]

        sep_color = gc.ui.colors[settings["separator_color"]]

    # Create a new list so we can preserve the server's channel order
    channel_logs = []

    for servlog in gc.server_log_tree:
        if servlog.server is gc.client.current_server:
            for chanlog in servlog.logs:
                channel_logs.append(chanlog)
            break

    channel_logs = quick_sort_channel_logs(channel_logs)

    leftWin.clear()

    # TODO: Incorperate servers into list
    for idx, clog in enumerate(channel_logs):
        # don't print categories or voice chats
        # TODO: this will break on private messages
        if clog.channel.type != ChannelType.text: continue
        text = clog.name
        length = len(text)

        offset = 0
        if settings["number_channels"]:
            offset = 3

        if length > left_win_width-offset:
            if settings["truncate_channels"]:
                text = text[0:left_win_width - offset]
            else:
                text = text[0:left_win_width - 3 - offset] + "..."

        leftWin.move(idx,0)
        if settings["number_channels"]:
            leftWin.addstr(str(idx+1) + ". ")
        if clog.channel is gc.client.current_channel:
            leftWin.addstr(text, gc.ui.colors[settings["current_channel_color"]])
        else:
            if clog.channel is not channel_logs[0]:
                pass

            if clog.unread and settings["blink_unreads"]:
                color = settings["unread_channel_color"]
                if "blink_" in color:
                    split = color.split("blink_")[1]
                    color = gc.ui.colors[split]|curses.A_BLINK
                elif "on_" in color:
                    color = gc.ui.colors[color.split("on_")[1]]
                leftWin.addstr(text, color)
            elif clog.mentioned_in and settings["blink_mentions"]:
                color = settings["unread_mention_color"]
                if "blink_" in color:
                    color = gc.ui.colors[color.split("blink_")[1]]
                leftWin.addstr(text, color)
            else:
                leftWin.addstr(text)

        # should the server have *too many channels!*, stop them
        # from spilling over the screen
        if idx  == gc.ui.max_y - 2 - settings["margin"]: break

    #with gc.term.location(0, start):
    #    print("".join(buffer))
    leftWin.refresh()

async def draw_user_win():
    userWin = gc.ui.userWin
    height, width = userWin.getmaxyx()

    userWin.clear()

    for idx,member in enumerate(gc.client.current_server.members):
        if idx+2 > height:
            userWin.addstr(idx,0, "(more)", gc.ui.colors["green"])
            break
        name = member.display_name
        if len(name) >= width:
            name = name[:width-4] + "..."

        userWin.addstr(idx,0, name)

    userWin.refresh()

async def draw_edit_win():
    editWin = gc.ui.editWin
    promptText = gc.client.prompt
    offset = len(promptText)+5

    borderColor = gc.ui.colors[settings["prompt_border_color"]]
    hasHash = False
    hashColor = 0
    promptColor = 0
    if gc.client.prompt != settings["default_prompt"]:
        hasHash = True
        hashColor = gc.ui.colors[settings["prompt_hash_color"]]
    promptColor = gc.ui.colors[settings["prompt_color"]]

    editWin.clear()
    editWin.addstr(0,0, "[", borderColor)
    if not hasHash:
        editWin.addstr(settings["default_prompt"], promptColor)
    else:
        editWin.addstr("#", hashColor)
        editWin.addstr(promptText, promptColor)
    editWin.addstr("]: ", borderColor)
    try:
        data = gc.ui.messageEdit.getCurrentData()
    except:
        data = ('', 0)
    editWin.addstr(0,offset, data[0])
    editWin.move(0,offset+data[1])

async def draw_serverlist():
    display = gc.ui.displayWin
    gc.ui.toggleDisplay()
    # Write serverlist to screen
    if len(gc.client.servers) == 0:
        display.addstr("Error: You are not in any servers.", gc.ui.colors["red"])
        while True:
            ch = display.getch()
            if ch == ord('q'):
                break
            asyncio.sleep(0.1)
        display.clear()
        gc.ui.toggleDisplay()
        return

    buf = []
    for slog in gc.server_log_tree:
        name = slog.name

        if slog.server is gc.client.current_server:
            buf.append((name, gc.ui.colors[settings["current_channel_color"]]))
            continue

        string = ""
        for clog in slog.logs:
            if clog.mentioned_in:
                attrs = curses.A_NORMAL
                color = settings["unread_mention_color"]
                if 'blink' in settings["unread_mention_color"]:
                    if settings["blink_mentions"]:
                        attrs = curses.A_BLINK
                    color = color.split('blink_')[1]
                string = (name, gc.ui.colors[color]|attrs)
                break
            elif clog.unread:
                attrs = curses.A_NORMAL
                color = settings["unread_channel_color"]
                if 'blink' in settings["unread_channel_color"]:
                    if settings["blink_unreads"]:
                        attrs = curses.A_BLINK
                    color = color.split('blink_')[1]
                string = (name, gc.ui.colors[color]|attrs)
                break

        if string == "":
            string = (name, gc.ui.colors[settings["text_color"]])

        buf.append(string)
    line_offset = 0
    while True:
        display.clear()
        display.addstr(0,0, "Available Servers:", gc.ui.colors["yellow"])
        display.hline(1,0, curses.ACS_HLINE, gc.ui.max_x)
        for serv_id, serv in enumerate(buf[line_offset:line_offset+(gc.ui.max_y-5)]):
            color = serv[1]
            display.addstr(2+serv_id,0, serv[0], color)
        display.addstr(2+serv_id+2,0, "(press q to quit this dialog)", gc.ui.colors["green"])
        ch = display.getch()
        if ch == ord('q'):
            break
        if len(buf) > (gc.ui.max_y-5):
            if ch == curses.KEY_UP:
                line_offset -= 1
            elif ch == curses.KEY_DOWN:
                line_offset += 1
            if line_offset < 0:
                line_offset = 0
            elif len(buf) > (gc.ui.max_y-5) and line_offset > (len(buf)-(gc.ui.max_y-5)):
                line_offset = len(buf)-(gc.ui.max_y-5)
        asyncio.sleep(0.1)
    gc.ui.toggleDisplay()
    gc.ui.refreshAll()
    gc.ui.doUpdate = True

async def draw_channellist():
    display = gc.ui.displayWin
    gc.ui.toggleDisplay()
    # Write serverlist to screen
    if len(gc.client.servers) == 0:
        display.addstr("Error: You are not in any servers.", gc.ui.colors["red"])
        while True:
            ch = display.getch()
            if ch == ord('q'):
                break
            asyncio.sleep(0.1)
        display.clear()
        gc.ui.toggleDisplay()
        return

    if len(gc.client.current_server.channels) == 0:
        display.addstr("Error: Does this server not have any channels?", gc.ui.colors["red"])
        while True:
            ch = display.getch()
            if ch == ord('q'):
                break
            asyncio.sleep(0.1)
        display.clear()
        gc.ui.toggleDisplay()
        return

    channels = quick_sort_channels(list(gc.client.current_server.channels))

    buf = []
    for channel in channels:
        if channel.type is ChannelType.text and \
                channel.permissions_for(channel.server.me).read_messages:
            buf.append((channel.name, 0))

    line_offset = 0
    while True:
        display.clear()
        display.addstr(0,0, "Available channels in ", gc.ui.colors["yellow"])
        display.addstr(gc.client.current_server.name, gc.ui.colors["magenta"])
        display.hline(1,0, curses.ACS_HLINE, gc.ui.max_x)
        for chan_id, chan in enumerate(buf[line_offset:line_offset+(gc.ui.max_y-5)]):
            color = chan[1]
            display.addstr(2+chan_id,0, chan[0], color)
        display.addstr(2+chan_id+2,0, "(press q to quit this dialog)", gc.ui.colors["green"])
        ch = display.getch()
        if ch == ord('q'):
            break
        if len(buf) > (gc.ui.max_y-5):
            if ch == curses.KEY_UP:
                line_offset -= 1
            elif ch == curses.KEY_DOWN:
                line_offset += 1
            if line_offset < 0:
                line_offset = 0
            elif len(buf) > (gc.ui.max_y-5) and line_offset > (len(buf)-(gc.ui.max_y-5)):
                line_offset = len(buf)-(gc.ui.max_y-5)
        asyncio.sleep(0.1)
    gc.ui.toggleDisplay()
    gc.ui.refreshAll()
    gc.ui.doUpdate = True

async def draw_emojilist():
    display = gc.ui.displayWin
    gc.ui.toggleDisplay()
    # Write serverlist to screen
    if len(gc.client.servers) == 0:
        display.addstr("Error: You are not in any servers.", gc.ui.colors["red"])
        while True:
            ch = display.getch()
            if ch == ord('q'):
                break
            asyncio.sleep(0.1)
        display.clear()
        gc.ui.toggleDisplay()
        return

    server_name = gc.client.current_server.name

    emojis = []
    server_emojis = None

    try: server_emojis = gc.client.current_server.emojis
    except: pass

    if server_emojis is not None and server_emojis != "":
        for emoji in server_emojis:
            emojis.append((':' + emoji.name + ':', gc.ui.colors["yellow"]))

    line_offset = 0
    while True:
        display.clear()
        display.addstr(0,0, "Available emojis in ", gc.ui.colors["yellow"])
        display.addstr(gc.client.current_server.name, gc.ui.colors["magenta"])
        display.hline(1,0, curses.ACS_HLINE, gc.ui.max_x)
        for emoji_id, emoji in enumerate(emojis[line_offset:line_offset+(gc.ui.max_y-5)]):
            color = emoji[1]
            display.addstr(2+emoji_id,0, emoji[0], color)
        display.addstr(2+emoji_id+2,0, "(press q to quit this dialog)", gc.ui.colors["green"])
        ch = display.getch()
        if ch == ord('q'):
            break
        if len(emojis) > (gc.ui.max_y-5):
            if ch == curses.KEY_UP:
                line_offset -= 1
            elif ch == curses.KEY_DOWN:
                line_offset += 1
            if line_offset < 0:
                line_offset = 0
            elif len(emojis) > (gc.ui.max_y-5) and line_offset > (len(emojis)-(gc.ui.max_y-5)):
                line_offset = len(emojis)-(gc.ui.max_y-5)
        asyncio.sleep(0.1)
    gc.ui.toggleDisplay()
    gc.ui.refreshAll()
    gc.ui.doUpdate = True

async def draw_userlist():
    display = gc.ui.displayWin
    gc.ui.toggleDisplay()
    if len(gc.client.servers) == 0:
        display.addstr("Error: You are not in any servers.", gc.ui.colors["red"])
        while True:
            ch = display.getch()
            if ch == ord('q'):
                break
            asyncio.sleep(0.1)
        display.clear()
        gc.ui.toggleDisplay()
        return

    if len(gc.client.current_server.channels) == 0:
        display.addstr("Error: Does this server not have any channels?", gc.ui.colors["red"])
        while True:
            ch = display.getch()
            if ch == ord('q'):
                break
            asyncio.sleep(0.1)
        display.clear()
        gc.ui.toggleDisplay()
        return

    nonroles = UserList(gc.ui.colors)
    admins = UserList(gc.ui.colors)
    mods = UserList(gc.ui.colors)
    bots = UserList(gc.ui.colors)
    everything_else = UserList(gc.ui.colors)

    for member in gc.client.current_server.members:
        if member is None: continue # happens if a member left the server

        if member.top_role.name.lower() == "admin":
            admins.add(member, " - (Admin)")
        elif member.top_role.name.lower() == "mod":
            mods.add(member, " - (Mod)")
        elif member.top_role.name.lower() == "bot":
            bots.add(member, " - (Bot)")
        elif member.top_role.is_everyone:
            nonroles.add(member, "")
        else:
            everything_else.add(member, " - " + member.top_role.name)


    # the final buffer that we're actually going to print
    buf = []

    if admins is not None:
        for user in admins.sort():
            buf.append(user)
    if mods is not None:
        for user in mods.sort():
            buf.append(user)
    if bots is not None:
        for user in bots.sort():
            buf.append(user)
    if everything_else is not None:
        for user in everything_else.sort():
            buf.append(user)
    if nonroles is not None:
        for user in nonroles.sort():
            buf.append(user)

    line_offset = 0
    while True:
        display.clear()
        display.addstr(0,0, "Members in ", gc.ui.colors["yellow"])
        display.addstr(gc.client.current_server.name, gc.ui.colors["magenta"])
        display.hline(1,0, curses.ACS_HLINE, gc.ui.max_x)
        for user_id, user in enumerate(buf[line_offset:line_offset+(gc.ui.max_y-5)]):
            color = user[1]
            display.addstr(2+user_id,0, user[0], color)
        display.addstr(2+user_id+2,0, "(press q to quit this dialog)", gc.ui.colors["green"])
        ch = display.getch()
        if ch == ord('q'):
            break
        if len(buf) > (gc.ui.max_y-5):
            if ch == curses.KEY_UP:
                line_offset -= 1
            elif ch == curses.KEY_DOWN:
                line_offset += 1
            if line_offset < 0:
                line_offset = 0
            elif len(buf) > (gc.ui.max_y-5) and line_offset > (len(buf)-(gc.ui.max_y-5)):
                line_offset = len(buf)-(gc.ui.max_y-5)
        asyncio.sleep(0.1)
    gc.ui.toggleDisplay()
    gc.ui.refreshAll()
    gc.ui.doUpdate = True

async def draw_help(terminateAfter=False):
    display = gc.ui.displayWin
    gc.ui.toggleDisplay()
    display.clear()
    buf = [
        [("Launch Arguments", gc.ui.colors["green"])],
        [("-----", gc.ui.colors["red"])],
        [("--copy-skeleton", gc.ui.colors["yellow"]),
            ('---', gc.ui.colors["cyan"]), ("copies template settings", 0)],
        [("This file can be found at ~/.config/Discline/config", gc.ui.colors["cyan"])],
        [],
        [("--store-token", gc.ui.colors["yellow"]),
            ('---', gc.ui.colors["cyan"]), ("stores your token", 0)],
        [("This file can be found at ~/.config/Discline/token", gc.ui.colors["cyan"])],
        [],
        [("--config", gc.ui.colors["yellow"]),
            ('---', gc.ui.colors["cyan"]), ("specify a specific config path", 0)],
        [],
        [("Available Commands", gc.ui.colors["green"])],
        [("-----", gc.ui.colors["red"])],
        [("/channel", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("switch to channel - (alias: c)", 0)],
        [("/server", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("switch server - (alias: s)", 0)],
        [("Note: These commands can now fuzzy-find!", gc.ui.colors["cyan"])],
        [],
        [("/servers", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("list available servers", 0)],
        [("/channels", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("list available channels", 0)],
        [("/users", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("list server users", 0)],
        [("/emojis", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("list server emojis", 0)],
        [],
        [("/nick", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("change your server nick", 0)],
        [("/game", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("change your game status", 0)],
        [("/file", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("upload a file via path", 0)],
        [("/status", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("change online presence", 0)],
        [("This can be either online, offline, away, or dnd", gc.ui.colors["cyan"])],
        [],
        [("/cX", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("shorthand to change channel (Ex: /c1)", 0)],
        [("This can be configured to start at 0 in your config", gc.ui.colors["cyan"])],
        [],
        [("/quit", gc.ui.colors["yellow"]),
            ('-', gc.ui.colors["cyan"]), ("exit Discline", 0)],
        [],
        [],
        [("(Press q to quit this dialog)", gc.ui.colors["green"])]
    ]

    line_offset = 0
    # needed for --help flag
    curses.cbreak()
    curses.noecho()
    while True:
        display.clear()
        for line_id, line in enumerate(buf[line_offset:line_offset+(gc.ui.max_y)]):
            display.move(line_id,0)
            for seg_id, segment in enumerate(line):
                if segment[0] == '-----':
                    display.addstr('-'*45, segment[1])
                    continue
                display.addstr(segment[0] + ' ', segment[1])
        ch = display.getch()
        if ch == ord('q'):
            break
        if len(buf) > (gc.ui.max_y-5):
            if ch == curses.KEY_UP:
                line_offset -= 1
            elif ch == curses.KEY_DOWN:
                line_offset += 1
            elif ch == curses.KEY_PPAGE:
                line_offset -= 5
            elif ch == curses.KEY_NPAGE:
                line_offset += 5
            if line_offset < 0:
                line_offset = 0
            elif len(buf) > (gc.ui.max_y-5) and line_offset > (len(buf)-(gc.ui.max_y-5)):
                line_offset = len(buf)-(gc.ui.max_y-5)
        asyncio.sleep(0.1)
    if terminateAfter:
        raise SystemExit
    gc.ui.toggleDisplay()
    gc.ui.refreshAll()
    gc.ui.doUpdate = True

async def draw_channel_log():
    chatWin = gc.ui.chatWin
    ft = None
    doBreak = False
    for server_log in gc.server_log_tree:
        if server_log.server is gc.client.current_server:
            for channel_log in server_log.logs:
                if channel_log.channel is gc.client.current_channel:
                    if channel_log.channel not in gc.channels_entered:
                        await gc.client.init_channel()
                        ft = gc.ui.views[channel_log.channel.id].formattedText
                        doBreak = True
                        break
                    # if the server has a "category" channel named the same
                    # as a text channel, confusion will occur
                    # TODO: private messages are not "text" channeltypes
                    if channel_log.channel.type != ChannelType.text: continue

                    ft = gc.ui.views[channel_log.channel.id].formattedText
                    if len(ft.messages) > 0 and channel_log.logs[-1].id == \
                            ft.messages[-1].id:
                        doBreak = True
                        break
                    if len(channel_log.logs) > 0:
                        ft.addMessage(channel_log.logs[-1])
                    doBreak = True
                    break
        if doBreak:
            break
    lines = ft.getLines()
    name_offset = 0
    chatWin_height, chatWin_width = chatWin.getmaxyx()
    # upon entering a new channel, scroll all the way down
    if gc.ui.channel_log_offset == -1 and len(lines) > chatWin_height:
        gc.ui.channel_log_offset = len(lines) - chatWin_height
    # check to see if scrolling is out of bounds
    elif len(lines) > chatWin_height and \
            gc.ui.channel_log_offset > len(lines)-chatWin_height:
        gc.ui.channel_log_offset = len(lines)-chatWin_height
    elif gc.ui.channel_log_offset <= -1:
        gc.ui.channel_log_offset = 0
    color = 0
    chatWin.clear()
    if not len(lines):
        chatWin.refresh()
        return
    for idx, line in enumerate(
            lines[gc.ui.channel_log_offset:gc.ui.channel_log_offset+chatWin_height]):
        if line.isFirst:
            author_color = await get_role_color(line.topRole, gc.ui.colors)
            chatWin.addstr(idx,0, line.user + ": ", author_color)
            name_offset = chatWin.getyx()[1]
        elif name_offset == 0:
            # if line is at the top and it's not a "user" line
            for subline in reversed(lines[0:gc.ui.channel_log_offset]):
                if subline.isFirst:
                    name_offset = len(subline.user) + 2
                    break
        chatWin.move(idx,name_offset)
        for idy, word in enumerate(line.words):
            color = 0
            if "@" + gc.client.current_server.me.display_name in word.content:
                color = gc.ui.colors[settings["mention_color"]]
            if not word.content:
                continue
            try:
                # if the next word attrs are the same
                if idy < len(line.words)-1 and word.attrs == line.words[idy+1].attrs:
                    chatWin.addstr(word.content + ' ', word.attrs|color)
                else:
                    chatWin.addstr(word.content, word.attrs|color)
                    chatWin.addstr(' ', curses.A_NORMAL)
            except:
                log("Text drawing failed at {}".format(word.content))
        chatWin.refresh()

