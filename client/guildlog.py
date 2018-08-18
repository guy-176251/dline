from discord import Guild
from client.channellog import ChannelLog

# Simple wrapper class to hold a list of ChannelLogs
class GuildLog():
    def __init__(self, guild, channel_log_list):
        self._guild = guild
        self._channel_logs = list(channel_log_list)

    @property
    def guild(self):
        return self._guild

    @property
    def name(self):
        return self._guild.name

    @property
    def logs(self):
        return self._channel_logs

    def clear_logs(self):
        for channel_log in self._channel_logs:
            del channel_log[:]

    # takes list of ChannelLog
    def add_logs(self, log_list):
        for logs in log_list:
            self._channel_logs.append(logs)
