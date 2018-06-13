import os
import sys
from yaml import safe_load, YAMLError
from blessings import Terminal

class OutdatedConfigException(Exception):
    pass

settings = ""

def copy_skeleton():
    term = Terminal()
    try:
        from shutil import copyfile
        if not os.path.exists(os.getenv("HOME") + "/.config/Discline"):
            os.mkdir(os.getenv("HOME") + "/.config/Discline")

        if os.path.exists(os.getenv("HOME") + "/.config/Discline/config"):
            try:
                os.remove(os.getenv("HOME") + "/.config/Discline/config")
            except:
                pass

        copyfile("res/settings-skeleton.yaml", os.getenv("HOME") + "/.config/Discline/config", follow_symlinks=True)
        print(term.green("Skeleton copied!" + term.normal))
        print(term.cyan("Your configuration file can be found at ~/.config/Discline"))

    except KeyboardInterrupt:
        print("Cancelling...")
        quit()
    except SystemExit:
        quit()
    except Exception as e:
        print("ERROR: Could not create skeleton file:", e)
        quit()

def load_config():
    arg = ""
    path = ""
    try:
        arg = sys.argv[1]
    except IndexError:
        pass
    if not path:
        try:
            if arg == "--config":
                path = sys.argv[2]
            else:
                path = os.getenv("HOME") + "/.config/Discline/config"
        except IndexError:
            print("ERROR: No path specified.")
            quit()
    global settings
    try:
        with open(path) as f:
            settings = safe_load(f)
        if "show_user_bar" not in settings:
            raise OutdatedConfigException
    except YAMLError:
        print("ERROR: Invalid config. Check and try again.")
        quit()
    except OutdatedConfigException:
        print("ERROR: Outdated config. Please update your config with --copy-skeleton and run again.")
        quit()
    except OSError:
        print("ERROR: Could not open config file.")
        quit()
    except:
        print("ERROR: Could not load config.")
        quit()

arg = ""
try:
    arg = sys.argv[1]
except IndexError:
    pass

doLoad = True
if arg == "--store-token" or arg == "--token":
    doLoad = False
elif arg == "--skeleton" or arg == "--copy-skeleton":
    copy_skeleton()
    quit()
if doLoad:
    load_config()
