from string import digits

def parse_numeric(string):
    if not string:
        return None
    if isinstance(string, float) or isinstance(string, int):
        return float(string)
    string = string.strip()
    try:
        parsed_value = float(string)
    except:
        parsed_value = None
    return parsed_value

