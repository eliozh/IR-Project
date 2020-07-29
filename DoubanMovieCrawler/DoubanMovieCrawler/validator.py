import re


def match_year(s):
    matches = re.findall(r'[\d]{4}', s)
    if matches:
        return matches[0]
    else:
        return '0'


def process_slash_str(s):
    alias = []
    items = s.split('/')
    for item in items:
        alias.append(item)
    return '/'.join(alias[0:30])
