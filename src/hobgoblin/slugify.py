import enum
import keyword
import re

try:
    from text_unidecode import unidecode
except ImportError:

    def unidecode(s):
        return s

import hobgoblin.enum as _enum


Case = _enum.make(nothing='N', lower='l', capital='C', upper='U')


class CaseStyle(enum.Enum):
    NOTHING = enum.auto()
    LOWER = enum.auto()
    CAPITAL = enum.auto()
    UPPER = enum.auto()


def trim_to_length(words, max_length):
    if max_length:
        new_words = []
        for word in words:
            if len(word) + len(new_words) <= max_length:
                max_length -= len(word)
                new_words.append(word)
            else:
                break
        if not new_words:
            new_words.append(words[0][:max_length])
        return new_words

    return words


def filter_out(words, drop):
    if drop:
        return [w for w in words if w not in drop]
    return words


def _remove_prefix(s, prefix):
    return s[len(prefix) :] if s.startswith(prefix) else s


def remove_prefix(words, prefix):
    return [_remove_prefix(w, prefix) for w in words]


def filter_out_prefix(words, prefix):
    return [w for w in words if not w.startswith(prefix)]


def filter_out_suffix(words, suffix):
    return [w for w in words if not w.endswith(suffix)]


def words_from_text(text, safe_chars, split_chars):
    # turn legit delimiting characters into spaces
    for ch in split_chars:
        if ch in text:
            text = text.replace(ch, " ")

    # make safe_chars into "words"
    assert " " not in safe_chars
    for ch in safe_chars:
        if ch in text:
            text = text.replace(ch, f" {ch} ")

    # remove runs of spaces and trim the ends
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    # return text split into words
    return [w if w in safe_chars else re.sub(r"\W", "", w) for w in text.split()]


@public
def for_identifier(
    text,
    to_ascii=True,
    case_style=CaseStyle.LOWER,
    split_chars=("_", "-", "."),
    stop_words=("the", "a", "an", "in", "is"),
    max_length=32,
    snake_case=True,
):
    if to_ascii:
        text = unidecode(text)

    words = words_from_text(text, (), split_chars)
    words = filter_out(words, stop_words)
    words = trim_to_length(words, max_length)

    if not words:
        raise ValueError("No words found")

    match case_style:
        case CaseStyle.LOWER:
            words = [x.casefold() for x in words]
        case CaseStyle.CAPITAL:
            words = [x.capitalize() for x in words]
        case CaseStyle.UPPER:
            words = [x.upper() for x in words]
        case _:
            pass

    if snake_case:
        ident = "_".join(words)
    else:
        ident = "".join(words)

    if keyword.iskeyword(ident):
        ident = f"{ident}_"

    assert ident.isidentifier()

    return ident


@public
def for_pathname(
    text,
    to_ascii=False,
    to_lower=True,
    split_chars=("_", "-", ".", "/"),
    safe_chars=("+",),
    stop_words=(),
    max_length=None,
    separator="_",
    capitalize=False,
):
    if to_ascii:
        text = unidecode(text)

    if to_lower:
        text = text.casefold()

    words = words_from_text(text, safe_chars, split_chars)
    words = filter_out(words, stop_words)
    words = trim_to_length(words, max_length)

    if not words:
        raise ValueError("")

    text = words.pop(0)
    prev_safe = text in safe_chars
    for w in words:
        if w in safe_chars:
            prev_safe = True
        elif not prev_safe:
            prev_safe = False
            text += separator
        else:
            prev_safe = False
        text += w

    if capitalize:
        # Don't change case of characters after the first
        text = text[0].upper() + text[1:]

    return text


@public
def for_git_branch(
    text,
    to_lower=False,
    split_chars=("-", ":", "..", ".", "@{", "\\"),
    safe_chars=("/",),
    stop_words=(),
    separator="-",
):
    text = unidecode(text)

    if to_lower:
        text = text.casefold()

    words = words_from_text(text, safe_chars, split_chars)
    words = filter_out(words, stop_words)
    words = trim_to_length(words, 40)

    if not words:
        raise ValueError("No words found")

    text = words.pop(0)
    prev_safe = text in safe_chars
    for w in words:
        if w in safe_chars:
            prev_safe = True
        elif not prev_safe:
            prev_safe = False
            text += separator
        else:
            prev_safe = False
        text += w

    return text.rstrip("/")
