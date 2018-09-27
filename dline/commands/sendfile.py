import curses
import time
from os import path
from getpass import getuser
import discord
from dline.utils.globals import gc
from dline.ui.ui import set_display

def send_file(filepath):

    # try to open the file exactly as user inputs it
    if path.exists(filepath):
        gc.client.wait_until_client_task_completes(\
                (gc.client.current_channel.send, {'file':discord.File(filepath)}))
    elif path.exists("/home/" + getuser() + "/" + filepath):
        # assume the user ommited the prefix of the dir path,
        # try to load it starting from user's home directory:
        filepath = "/home/" + getuser() + "/" + filepath
        gc.client.wait_until_client_task_completes(\
                (gc.client.current_channel.send, {'file':discord.File(filepath)}))
    else:
        # Either a bad file path, the file was too large,
        # or encountered a connection problem during upload
        msg = "Error: Bad filepath"
        set_display(msg, curses.A_BOLD|gc.ui.colors["red"])
