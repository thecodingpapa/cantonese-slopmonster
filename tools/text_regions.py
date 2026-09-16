"""Small, conservative script-region reader; not a full Markdown parser."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    start: int
    end: int
    kind: str


def is_han(char):
    n = ord(char)
    return (0x3400 <= n <= 0x4DBF or 0x4E00 <= n <= 0x9FFF
            or 0xF900 <= n <= 0xFAFF or 0x20000 <= n <= 0x323AF)


def regions(text, markdown=True, include_quotes=False):
    """Return non-overlapping exclusions plus parser warnings, in source offsets."""
    found, warnings = [], []
    taken = bytearray(len(text))

    def add(start, end, kind):
        # Protect uncovered parts too: a quote can contain an inline code span.
        cursor = start
        while cursor < end:
            if taken[cursor]:
                cursor += 1
                continue
            stop = cursor + 1
            while stop < end and not taken[stop]:
                stop += 1
            found.append(Region(cursor, stop, kind))
            taken[cursor:stop] = b'\x01' * (stop - cursor)
            cursor = stop

    if markdown:
        fence = None
        offset = 0
        for line in text.splitlines(keepends=True):
            if fence:
                if re.match(r'^ {0,3}' + re.escape(fence[0]) + '{' + str(fence[1]) + r',}\s*$', line):
                    add(fence[2], offset + len(line), 'code')
                    fence = None
            else:
                m = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
                if m:
                    fence = (m[1][0], len(m[1]), offset)
            offset += len(line)
        if fence:
            add(fence[2], len(text), 'code')
            warnings.append('未結束嘅程式碼區塊；餘下內容冇接受語體檢查。')
        for m in re.finditer(r'(`+)([^`]|(?!\1)`)*?\1', text):
            add(m.start(), m.end(), 'code')
        for m in re.finditer(r'(?m)^ {0,3}(?:#{1,6}\s+|>\s?).*$', text):
            # A Markdown blockquote is a quotation, unless explicitly included.
            if include_quotes and re.match(r'^ {0,3}>', m[0]):
                continue
            add(m.start(), m.end(), 'heading' if m[0].lstrip().startswith('#') else 'quote')
        for m in re.finditer(r'!\[[^\]\n]*\]\([^\)\n]*\)', text):
            add(m.start(), m.end(), 'image')
        for m in re.finditer(r'\]\(([^\)\n]+)\)', text):
            add(m.start(1), m.end(1), 'link_target')
        for m in re.finditer(r'<!--.*?-->', text, re.S):
            add(m.start(), m.end(), 'comment')

    if not include_quotes:
        pairs = {'「': '」', '『': '』', '“': '”', '‘': '’', '"': '"'}
        i = 0
        while i < len(text):
            if taken[i] or text[i] not in pairs:
                i += 1
                continue
            start, stack = i, [pairs[text[i]]]
            i += 1
            while i < len(text) and stack:
                if not taken[i]:
                    if text[i] == stack[-1]:
                        stack.pop()
                    elif text[i] in pairs and text[i] != '"':
                        stack.append(pairs[text[i]])
                i += 1
            if stack:
                warnings.append('未配對嘅引號；請修正標記後重跑。')
                # Leave malformed quoted prose visible instead of hiding the rest.
            else:
                add(start, i, 'quote')
        for m in re.finditer(r"(?<![\w])'[^'\n]+'(?![\w])", text):
            add(m.start(), m.end(), 'quote')

    cue = r'(?:\d{1,2}:\d{2}(?::\d{2})?|畫面|字幕|音效|音樂|停頓|鏡頭|轉場|B-roll|SFX|CUT)'
    for m in re.finditer(r'(?:\[|【)' + cue + r'[^\]\n】]*(?:\]|】)', text, re.I):
        add(m.start(), m.end(), 'cue')
    for m in re.finditer(r'https?://[^\s<>\]\)」』”。，；！？]+', text):
        add(m.start(), m.end(), 'url')
    return sorted(found, key=lambda r: r.start), warnings


def narration(text, markdown=True, include_quotes=False):
    spans, warnings = regions(text, markdown, include_quotes)
    chars = list(text)
    for r in spans:
        # NUL barriers preserve source positions and prevent matches across exclusions.
        chars[r.start:r.end] = ['\n' if c == '\n' else '\0' for c in text[r.start:r.end]]
    return ''.join(chars), spans, warnings


def read_utf8(path):
    from pathlib import Path
    return Path(path).read_text(encoding='utf-8-sig')
