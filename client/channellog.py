from discord import TextChannel, DMChannel

# Wrapper class to make dealing with logs easier
class ChannelLog():
    def __init__(self, channel, logs):
        self.unread = False
        self.mentioned_in = False
        self._channel = channel
        self._logs = list(logs)

    @property
    def guild(self):
        return self._channel.guild

    @property
    def channel(self):
        return self._channel

    @property
    def logs(self):
        return self._logs

    @property
    def name(self):
        if isinstance(self._channel, TextChannel):
            return self._channel.name
        elif isinstance(self._channel, DMChannel):
            name = self._channel.name
            if name is None:
                name = self_channel.recipients[0].name
            return name
        else:
            return "Name unavailable"

    @property
    def index(self):
        if isinstance(self._channel, TextChannel):
            return self._channel.position

    def append(self, message):
        self._logs.append(message)

    def insert(self, i, message):
        self._logs.insert(i, message)

    def __len__(self):
        return len(self._logs)
