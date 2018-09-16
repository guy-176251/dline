from dline.ui.formattedText import FormattedText

class View:
    def __init__(self, name):
        self.name = name
        self.topWinContent = None
        self.leftWinContent = None
        self.userWinContent = None
        self.formattedText = FormattedText()

def init_view(gc, channel):
    gc.ui.views[str(channel.id)] = View(channel.name)
