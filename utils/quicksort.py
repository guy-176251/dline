
def quick_sort_channels(channels):
    # sort channels to match the guild's default chosen positions
    if len(channels) <= 1: return channels
    else:
        return quick_sort_channels([e for e in channels[1:] \
            if e.position <= channels[0].position]) + \
            [channels[0]] + quick_sort_channels([e for e in channels[1:] \
            if e.position > channels[0].position])

def quick_sort_channel_logs(channel_logs):
    # sort channels to match the guild's default chosen positions
    if len(channel_logs) <= 1: return channel_logs
    else:
        return quick_sort_channel_logs([e for e in channel_logs[1:] \
            if e.channel.position <= channel_logs[0].channel.position]) + \
            [channel_logs[0]] + quick_sort_channel_logs([e for e in channel_logs[1:] \
            if e.channel.position > channel_logs[0].channel.position])
