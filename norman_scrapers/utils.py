import re
from datetime import datetime

def extract_integer(s):
    match = re.match(r'(\d+)', s)
    if match:
        return int(match.group(1))
    else:
        return s
    
def string_to_timestamp(date_str):
    current_year = datetime.now().year
    date_object = datetime.strptime(f"{current_year} {date_str}", "%Y %B, %a. %d")
    return date_object.isoformat()