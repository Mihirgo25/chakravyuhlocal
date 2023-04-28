from string import digits

def parse_numeric(string):
    if not string:
        return None
    if isinstance(string, float) or isinstance(string, int):
        return float(string)
    string = string.strip()
    decimal_point = None
    negative_check = False
    parsed_value = 0
    if string.startswith('-'):
        string = string[1:]
        negative_check = True
    for ch in string:
        if ch == '.':
            if decimal_point is not None:
                return None
            else:
                decimal_point = 0
                continue
        if ch not in digits:
            return None
        if decimal_point is not None:
            decimal_point += 1
        parsed_value = parsed_value*10 + ord(ch) - ord('0')
    if decimal_point is not None:
        parsed_value = parsed_value / 10**decimal_point
    parsed_value = float(parsed_value)
    return parsed_value if not negative_check else -parsed_value

