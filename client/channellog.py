from discord import ChannelType

# Wrapper class to make dealing with logs easier
class ChannelLog():
    def __init__(self, channel, logs):
        self.unread = False
        self.mentioned_in = False
        self._channel = channel
        self._logs = list(logs)

    @property
    def server(self):
        return self._channel.server

    @property
    def channel(self):
        return self._channel

    @property
    def logs(self):
        return self._logs

    @property
    def name(self):
        if self._channel.type == ChannelType.text:
            return self._channel.name
        elif self._channel.type == ChannelType.private:
            name = self._channel.name
            if name is None:
                name = self_channel.recipients[0].name
            return name
        else:
            return "Name unavailable"

    @property
    def index(self):
        if self._channel.type == ChannelType.text:
            return self._channel.position

    def get_server(self): return self._channel.server #TODO: Delete
    def get_channel(self): return self._channel #TODO: Delete

    def get_logs(self): #TODO: Delete
        return self._logs

    def get_name(self): #TODO: Delete
        return self._channel.name

    def get_server_name(self): #TODO: Delete
        return self._channel.server.name

    def append(self, message):
        self._logs.append(message)

    def index(self, message): #TODO: Delete
        return self._logs.index(message)

    def insert(self, i, message):
        self._logs.insert(i, message)

    def __len__(self):
        return len(self._logs)

    def len(self): #TODO: Delete
        return len(self._logs)

    def get_index(self): #TODO: Delete
        return self._index

    def set_index(self, int): #TODO: Delete
        self._index = int

    def inc_index(self, int): #TODO: Delete
        self._index += int

    def dec_index(self, int): #TODO: Delete
        self._index -= int
