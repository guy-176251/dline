import re
import sys
import curses
from io import StringIO
from mistletoe.block_token import (BlockToken, Paragraph as _Paragraph,
        CodeFence)
from mistletoe.block_tokenizer import tokenize as blockTokenize
from mistletoe.span_token import (RawText, SpanToken, InlineCode,
        Strong, Emphasis,_first_not_none_group)
from mistletoe.span_tokenizer import tokenize as spanTokenize

hasItalic = False
if sys.version_info >= (3,7):
    hasItalic = True

def rectifyText(obj):
    text = obj
    if type(text) != str:
        text = obj.read()
    lines = []
    for line in text.splitlines():
        if '```' in line and line != '```':
            if line.startswith('```'):
                # Line contains ``` at beginning or middle
                lines.append('```')
                lines.append(line.replace('```', '').lstrip())
            elif line.endswith('```'):
                # Line ends with ```
                lines.append(line.replace('```', ''))
                lines.append('```')
            else:
                split = line.split('```')
                lines.append(split[0])
                lines.append('```')
                lines.append(split[1])
            continue
        lines.append(line)
    rectMsg = '\n'.join(lines)
    if len(rectMsg) > 0 and rectMsg[-1] != '\n':
        rectMsg = rectMsg + '\n'
    return rectMsg

def parseText(msg, colors):
    spanTokens = []
    shrugPresent = False
    # code really should only have ascii in it
    if "¯\_(ツ)_/¯" in msg:
        shrugPresent = True
    # Needed for the markdown to parse correctly
    msg = StringIO(rectifyText(msg))
    doc = Document(msg)
    blockTokens = doc.children
    #log("blockTokens: {}".format(blockTokens))
    for tokid, blockToken in enumerate(blockTokens):
        # These are blockToken objects
        # A blockToken object has a LIST of children
        for child in blockToken.children:
            if blockToken.__class__.__name__ == "CodeFence":
                spanTokens.append((child.content, curses.A_REVERSE))
                continue
            attrs = curses.A_NORMAL
            subChild = child
            while subChild.__class__ != RawText:
                if subChild.__class__ == StrongEmphasis:
                    if hasItalic:
                        attrs |= curses.A_BOLD|curses.A_ITALIC
                    else:
                        attrs |= curses.A_BOLD|curses.A_UNDERLINE
                elif subChild.__class__ == Strong:
                    attrs |= curses.A_BOLD
                elif subChild.__class__ == Emphasis:
                    if hasItalic:
                        attrs |= curses.A_ITALIC
                    else:
                        attrs |= curses.A_UNDERLINE
                elif subChild.__class__ == Underlined:
                    attrs |= curses.A_UNDERLINE
                elif subChild.__class__ == URL:
                    attrs |= curses.A_UNDERLINE | colors["blue"]
                elif subChild.__class__ == InlineCode:
                    attrs |= curses.A_REVERSE
                subChild = subChild.children[0]
            if shrugPresent and subChild.content.startswith('¯'):
                spanTokens.append(("¯\_(ツ)_/¯", curses.A_NORMAL))
                return spanTokens
            spanTokens.append((subChild.content, attrs))

    return spanTokens

class Document(BlockToken):
    """
    Document token.
    """
    def __init__(self, lines):
        self.footnotes = {}
        # Document tokens have immediate access to first-level block tokens.
        # Useful for footnotes, etc.
        self.children = blockTokenize(lines, [CodeFence, Paragraph], parent=None)

def tokenize_inner(content):
    return spanTokenize(content, [URL, StrongEmphasis, Underlined, Strong, Emphasis, InlineCode, RawText])

class URL(SpanToken):
    """
    URL tokens. ("http://example.com")
    """
    pattern = re.compile("(http(s)?:\\/\\/.)?(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%_\\+.~#?&//=]*)")
    def __init__(self, match_obj):
        self.children = (RawText(match_obj.group()),)

class Underlined(SpanToken):
    """
    Underlined tokens. ("__some text__")
    """
    pattern = re.compile(r"\_\_([^\s*].*?)\_\_|\b__([^\s_].*?)__\b")
    def __init__(self, match_obj):
        self.children = tokenize_inner(_first_not_none_group(match_obj))

class StrongEmphasis(SpanToken):
    """
    Strong-Emphasis tokens. ("***some text***")
    """
    pattern = re.compile(r"(?:\*\*\*|\_\*\*|\*\*\_)([^\s]*?)(?:\*\*\*|\_\*\*|\*\*\_)|\b__([^\s_].*?)__\b")
    def __init__(self, match_obj):
        self.children = tokenize_inner(_first_not_none_group(match_obj))

class Paragraph(_Paragraph):
    def __init__(self, lines):
        content = ''.join([line.lstrip() for line in lines]).strip()
        BlockToken.__init__(self, content, tokenize_inner)

    @classmethod
    def read(cls, lines):
        line_buffer = [next(lines)]
        next_line = lines.peek()
        while (next_line is not None
                and next_line.strip() != ''
                and not CodeFence.start(next_line)):
            line_buffer.append(next(lines))
            next_line = lines.peek()
        return line_buffer
