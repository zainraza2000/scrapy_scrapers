import re

def extract_integer(s):
    match = re.match(r'(\d+)', s)
    if match:
        return int(match.group(1))
    else:
        return s