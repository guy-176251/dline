import curses

# TODO: Make drawing methods draw the name and slice buffer
class MessageEdit:
    SCROLL = 20
    def __init__(self):
        self.curPos = 0
        self.inputBuffer = []

    def reset(self):
        self.curPos = 0
        del(self.inputBuffer[:])

    def getCurrentData(self):
        return (bytearray(self.inputBuffer).decode("utf-8"), self.curPos)

    def addKey(self, ch):
        # check if character is function character
        # Home, End, Left/Up, Right/Down, Enter
        if ch == curses.KEY_HOME:
            self.curPos = 0
        elif ch == curses.KEY_END:
            # if inputBuffer fits into line
            self.curPos = len(self.inputBuffer)
        elif ch == curses.KEY_LEFT:
            # curPos is greater than 0
            if self.curPos > 0:
                self.curPos -= 1
        elif ch == curses.KEY_RIGHT:
            # less than end of buffer and less than EOL
            if self.curPos < len(self.inputBuffer):
                self.curPos += 1
        elif ch == curses.KEY_UP or ch == curses.KEY_DOWN:
            pass
        elif ch in (0x7f, ord('\b'), curses.KEY_BACKSPACE):
            if self.curPos > 0:
                self.inputBuffer.pop(self.curPos-1)
                self.curPos -= 1
        elif ch == ord('\n'):
            return bytearray(self.inputBuffer).decode("utf-8")
        # Normal text
        else:
            self.inputBuffer.insert(self.curPos, ch)
            self.curPos += 1
