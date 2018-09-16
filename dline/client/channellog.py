from discord import TextChannel, GroupChannel, DMChannel, abc, iterators

class PrivateChannel(abc.Messageable):
    def __init__(self, channel, guild, position):
        self._channel = channel
        self.name = ""
        self.topic = ""
        self.members = None
        if isinstance(channel, DMChannel):
            self.name = channel.recipient.name
            self.members = (channel.me, channel.recipient)
        elif isinstance(channel, GroupChannel):
            self.members = []
            for user in channel.recipients:
                self.members.append(user)
            self.name = "Group " + str(position)
            if channel.name is not None:
                self.name = channel.name
        self.topic = self.name
        self.id = position
        self.me = channel.me
        self.guild = guild
        self.position = position

    def history(self, *args, **kwargs):
        return iterators.HistoryIterator(self._channel, limit=100)

    def permissions_for(self, *args, **kwargs):
        self._channel.permissions_for(*args, **kwargs)

    async def send(self, *args, **kwargs):
        await self._channel.send(*args, **kwargs)

    async def trigger_typing(self):
        await self._channel.trigger_typing()

    async def _get_channel(self):
        return self

    def __aiter__(self):
        return self

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
        if isinstance(self._channel, TextChannel) or \
                isinstance(self._channel, PrivateChannel):
            return self._channel.name

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
