import threading
import curses
import time

from utils.log import log
from ui.ui import CursesUi

class UiThread(threading.Thread):
    def __init__(self, gc):
        self.gc = gc
        super().__init__()
        self.ui = CursesUi(threading.Lock())
        self.funcs = []

    def run(self):
        log("Starting UI thread")
        curses.wrapper(self.ui.run)
        while not self.gc.doExit:
            if len(self.funcs) > 0:
                self.funcs.pop()()
            time.sleep(0.01)
        log("Exiting UI thread")
