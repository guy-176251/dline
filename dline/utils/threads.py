import threading
import curses
import time

from dline.utils.log import log
from dline.ui.ui import CursesUi

class WorkerThread(threading.Thread):
    def __init__(self, gc, func):
        self.gc = gc
        self.func = func
        super().__init__()

    def run(self):
        log("Starting {} thread".format(self.func.__name__))
        try:
            self.func()
        except Exception as e:
            log("Error in {}: {}".format(self.func.__name__, e))

class UiThread(threading.Thread):
    def __init__(self, gc):
        self.gc = gc
        self.ui = CursesUi(threading.Lock())
        self.funcs = []
        self.locks = []
        super().__init__()

    def run(self):
        log("Starting UI thread")
        curses.wrapper(self.ui.run)
        self.locks = []
        while not self.gc.doExit:
            try:
                if len(self.funcs) > 0:
                    call = self.funcs.pop()
                    func = call[0]
                    self.locks.append(func.__name__)
                    args = []
                    if len(call) > 1:
                        args = call[1:]
                    func(*args)
                    self.locks.remove(func.__name__)
                time.sleep(0.01)
            except Exception as e:
                log("Error: {}".format(e))
        log("Exiting UI thread")
