from datetime import timedelta
import re
from discord import MessageType, Member

def get_role_color(r, gc):
    color = ""
    try:
        for role in gc.settings["custom_roles"]:
            if r == role["name"].lower():
                color = gc.ui.colors[role["color"]]

        if color is not "": # The user must have already been assigned a custom role
            pass
        elif gc.settings["normal_user_color"] is not None:
            color = gc.ui.colors[gc.settings["normal_user_color"]]
        else: color = gc.ui.colors["green"]
    # if this fails, the user either left or was banned
    except:
        if gc.settings["normal_user_color"] is not None:
            color = gc.ui.colors[gc.settings["normal_user_color"]]
        else: color = gc.ui.colors["green"]
    return color

def calc_mutations(msg):
    for embed in msg.embeds:
        info = "\n---\n"
        if embed.description:
            info += embed.description
        elif embed.title:
            info += embed.title

        msg.content += info

    try: # if the message is a file, extract the discord url from it
        json = str(msg.attachments[0]).split("'")
        for string in json:
            if string is not None and string != "":
                if "cdn.discordapp.com/attachments" in string:
                    msg.content = string
                    break
    except IndexError: pass

    # if message is blank and message's timestamp is within a second
    # of a member's join timestamp, it's a join message
    if not msg.content and type(msg.author) == Member:
        timeDiff = msg.created_at - msg.author.joined_at
        if timedelta(seconds=-1) <= timeDiff <= timedelta(seconds=1):
            msg.content = "**({} joined the guild!)**".format(msg.author.display_name)

            return msg

    text = msg.content

    # check to see if it has any custom-emojis
    # These will look like <:emojiname:39432432903201>
    # We will recursively trim this into just :emojiname:
    try:
        if msg.guild.emojis is not None and len(msg.guild.emojis) > 0:
            for emoji in msg.guild.emojis:
                full_name = "<:" + emoji.name + ":" + str(emoji.id) + ">"

                while full_name in text:
                    text = trim_emoji(full_name, emoji.name, text)

            msg.content = text
    except: pass

    # Catch all of the non-guild (nitro) emojis
    mat = re.match('<.*:\w*:\d*>', text)
    if mat is not None:
        full_name = mat.group(0)

        while full_name in text:
            text = trim_emoji(full_name, full_name[1:-1].split(':')[1], text)

        msg.content = text

    # check if the message is a "user has pinned..." message
    if msg.type == MessageType.pins_add:
        msg.content = convert_pin(msg)

    # else it must be a regular message, nothing else
    return msg

def convert_pin(msg):
    name = ""
    if msg.author.nick is not None and msg.author.nick != "":
        name = msg.author.nick
    else: name = msg.author.name
    return "{} {} has pinned a message to this channel.".format(chr(0x1f4cc), name)

def trim_emoji(full_name, short_name, string):
    return string.replace(full_name, ":" + short_name + ":")
