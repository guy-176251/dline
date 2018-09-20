import os
from yaml import safe_load, YAMLError
from blessings import Terminal
from dline.utils.globals import OutdatedConfigException

def copy_skeleton():
    term = Terminal()
    skeleton_path = get_settings_skeleton()
    try:
        from shutil import copyfile
        if not os.path.exists(os.getenv("HOME") + "/.config/dline"):
            os.makedirs(os.getenv("HOME") + "/.config/dline", exist_ok=True)

        if os.path.exists(os.getenv("HOME") + "/.config/dline/config.yaml"):
            try:
                os.remove(os.getenv("HOME") + "/.config/dline/config.yaml")
            except:
                pass

        copyfile(skeleton_path, os.getenv("HOME") + \
                "/.config/dline/config.yaml", follow_symlinks=True)
        print("Skeleton copied!")
        print("Your configuration file can be found at ~/.config/dline")

    except KeyboardInterrupt:
        print("Cancelling...")
        quit()
    except SystemExit:
        quit()
    except Exception as e:
        print("ERROR: Could not create skeleton file:", e)
        quit()

def load_config(gc, config_path=None):
    gc.settings = {}
    path = os.getenv("HOME") + "/.config/dline/config.yaml"
    if config_path is not None:
        path = config_path
    try:
        with open(path) as f:
            gc.settings = safe_load(f)
            if gc.settings is None:
                gc.settings = {}
            gc.settings = fill_values(gc.settings)
        if "show_user_bar" in gc.settings:
            raise OutdatedConfigException
    except YAMLError:
        print("ERROR: Invalid config. Check and try again.")
        quit()
    except OutdatedConfigException:
        print("ERROR: Outdated config. Please update your config with --copy-skeleton and run again.")
        quit()
    except OSError:
        # no config file present
        gc.settings = fill_values({})
    except Exception as e:
        print("ERROR: Could not load config: {}".format(e))
        quit()

def fill_values(config_dict):
    s = config_dict
    with open(get_settings_skeleton()) as f:
        s_def = safe_load(f)
    for key,value in s_def.items():
        if key not in config_dict:
            s[key] = value
    return s

def get_settings_skeleton():
    import dline
    return os.path.dirname(dline.__file__)+"/res/settings-skeleton.yaml"
