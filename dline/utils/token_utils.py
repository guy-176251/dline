import os
from dline.utils.globals import gc

def get_token():
    if os.path.exists(os.getenv("HOME") + "/.config/dline/token"):
        token = ""
        try:
            f = open(os.getenv("HOME") + "/.config/dline/token", "r")
            token = f.read().strip()
            f.close()
        except: pass

        if token != "":
            return token

    from blessings import Terminal
    gc.term = Terminal()
    print("\n" + gc.term.red("Error reading token."))
    print("\n" + gc.term.yellow("Are you sure you stored your token?"))
    print(gc.term.yellow("Use --store-token to store your token."))
    quit()

def store_token():
    import sys
    from blessings import Terminal

    token = ""
    try:
        token=sys.argv[2]
    except IndexError:
        print("Token not specified in arguments. Reading from stdin.")
        while True:
            token = input().strip()
            if len(token) == 0:
                print("Please enter a valid token!")
                continue
            break

    if not os.path.exists(os.getenv("HOME") + "/.config/dline"):
        os.mkdir(os.getenv("HOME") + "/.config/dline")

    if token is not None and token != "":
        # trim off quotes if user added them
        token = token.strip('"').strip("'")

    try:
        f = open(os.getenv("HOME") + "/.config/dline/token", "w")
        f.write(token)
        f.close()
        print(Terminal().green("Token stored!"))
    except:
        print(Terminal().red("Error: Could not write token to file."))
        quit()
