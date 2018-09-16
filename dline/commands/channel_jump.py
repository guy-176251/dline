from dline.utils.globals import gc
from dline.utils.quicksort import quick_sort_channel_logs

def channel_jump(arg):
    logs = []

    num = int(arg[1:]) - 1

    # sub one to allow for "/c0" being the top channel
    if gc.settings["arrays_start_at_zero"]:
        num -= 1

    # in case someone tries to go to a negative index
    if num <= -1:
        num = 0

    for slog in gc.guild_log_tree:
        if slog.guild is gc.client.current_guild:
            for clog in slog.logs:
                logs.append(clog)

    logs = quick_sort_channel_logs(logs)


    if num > len(logs): num = len(logs) - 1

    gc.client.current_channel = logs[num].name
    logs[num].unread = False
    logs[num].mentioned_in = False
    gc.ui.channel_log_offset = -1
