import os
from yaml import safe_load, YAMLError
from blessings import Terminal
from utils.globals import OutdatedConfigException

def copy_skeleton():
    term = Terminal()
    try:
        from shutil import copyfile
        if not os.path.exists(os.getenv("HOME") + "/.config/Discline"):
            os.makedirs(os.getenv("HOME") + "/.config/Discline", exist_ok=True)

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

def load_config(gc, config_path=None):
    path = os.getenv("HOME") + "/.config/Discline/config"
    if config_path is not None:
        path = config_path
    try:
        with open(path) as f:
            gc.settings = safe_load(f)
        if "show_user_win" not in gc.settings:
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
