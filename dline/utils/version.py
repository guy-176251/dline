def check_versions():
    pass_check = True
    instructions = "Please install the correct dependencies with: " +\
            "pip install --user -r requirements.txt"
    import discord
    import mistletoe
    if discord.version_info < (1,0,0):
        print("You are not using discord.py rewrite!")
        pass_check = False
    _version = mistletoe.__version__.split('.')
    version = []
    for v in _version:
        version.append(int(v))
    if tuple(version) != (0,6,2):
        print("You are not using mistletoe 0.6.2!")
        pass_check = False

    return pass_check
