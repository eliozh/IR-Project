import string


def match_words(s):
    for c in s:
        if '\u4e00' <= c <= '\u9fff':
            continue
        if c in string.ascii_letters + string.digits:
            continue
        return False
    return True
