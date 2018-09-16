import curses
from collections import deque
import unicodedata
from dline.utils.globals import gc
from dline.ui.textParser import parseText

def findWidth(s):
    width = 0
    for c in s:
        w = unicodedata.east_asian_width(c)
        if w in ('N', 'Na', 'H', 'A'):
            width += 1
        else:
            width += 2
    return width

class TokenContainer:
    def __init__(self, content, attrs):
        self.content = content
        self.clean_content = content
        self.attrs = attrs

class MessageContainer:
    def __init__(self, name, lines):
        self.name = name
        self.lines = lines

class Line:
    def __init__(self, isFirst=False, user=None, topRole=None):
        self.words = []
        if isFirst:
            if user is None:
                raise Exception
        self.user = user
        self.topRole = topRole
        self.isFirst = isFirst

    def add(self, token):
        self.words.append(token)

class FormattedText:
    def __init__(self):
        self.messages = []
        self.messageBuffer = deque([], gc.settings["max_messages"])

    def addMessage(self, msg):
        self.messages.append(msg)
        self.format(msg)

    def getLines(self):
        lines = []
        for message in self.messageBuffer:
            for line in message.lines:
                lines.append(line)
        return lines

    def refresh(self):
        self.messageBuffer.clear()
        for msg in self.messages:
            self.format(msg)

    def format(self, msg):
        try:
            name = msg.author.display_name
        except:
            name = msg.author.name
            if name is None:
                name = "Unknown Author"
        topRole = ""
        if msg.author.__class__.__name__ == "Member":
            topRole = msg.author.top_role.name.lower()
        offset = findWidth(name)+2
        width = gc.ui.chatWinWidth-offset

        complete_msg = [msg.clean_content]
        if msg.attachments:
            for attachment in reversed(msg.attachments):
                complete_msg.append(attachment.url)
        # Tokens grouped by type (type tokens)
        ttokens = parseText("\n".join(complete_msg), gc.ui.colors)
        #log("ttokens: {}".format(ttokens))
        # Separate tokens by word (word tokens)
        wtokens = []
        for tok_id, ttoken in enumerate(ttokens):
            # handle newlines
            if '\n' in ttoken[0].strip() and ttoken[0] != '\n':
                lines = ttoken[0].splitlines()
                #log("lines: {}".format(lines))
                if not lines[0]: # if first line is empty
                    wtokens.append(('\n', curses.A_NORMAL))
                    del lines[0]
                for lineid, line in enumerate(lines):
                    for word in line.split(' '):
                        wtokens.append((word, ttoken[1]))
                    if lineid != len(lines)-1 or (lineid == len(lines)-1 and ttoken[0].endswith('\n')):
                        wtokens.append(('\n', curses.A_NORMAL))
                continue
            # process ttoken into wtokens
            words = ttoken[0].split(' ')
            idx = 0
            while idx < len(words):
                word = words[idx]
                wordwidth = findWidth(word)
                if wordwidth < 1:
                    idx += 1
                    continue
                # group mentions together
                if word.startswith('@'):
                    words_ss = words[idx:] # words subsection
                    for i in reversed(range(len(words_ss))):
                        segment = words_ss[:i+1]
                        if not segment[0]:
                            continue
                        if " ".join(segment)[1:].lower() in msg.guild.me.display_name.lower():
                            for ss_word in segment:
                                words.remove(ss_word)
                            words.insert(idx, " ".join(segment))
                            word = words[idx]
                            wordwidth = findWidth(word)
                            break
                # if single word is longer than width
                if wordwidth >= width:
                    iters = wordwidth//(width-1)
                    if wordwidth%(width-1) != 0:
                        iters += 1
                    for segid in range(iters):
                        iterlen = int(width*(len(word)/wordwidth))
                        if segid < iters-1:
                            rng = word[segid*(iterlen-1):(segid+1)*(iterlen-1)]
                            wtokens.append((rng, ttoken[1]))
                            wtokens.append(('\n', curses.A_NORMAL))
                        else:
                            rng = word[segid*(iterlen-1):]
                            wtokens.append((rng, ttoken[1]))
                    idx += 1
                    continue
                wtokens.append((word, ttoken[1]))
                idx += 1
        #log("wtokens: {}".format(wtokens))
        cpos = 0
        line = Line(True, name, topRole)
        ltokens = []
        for idx,wtoken in enumerate(wtokens):
            wtokenlen = findWidth(wtoken[0])
            cpos += wtokenlen+1
            if cpos > width or wtoken[0] == '\n':
                ltokens.append(line)
                line = Line()
                line.add(TokenContainer(wtoken[0].rstrip(), wtoken[1]))
                cpos = wtokenlen+1
                continue
            line.add(TokenContainer(wtoken[0].rstrip(), wtoken[1]))
            if idx == len(wtokens)-1:
                ltokens.append(line)
        mc = MessageContainer(name, ltokens)
        self.messageBuffer.append(mc)
