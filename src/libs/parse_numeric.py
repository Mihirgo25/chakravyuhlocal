from string import digits

def parse_numeric(string):
    if not string:
        return None
    string = string.strip()
    decimal_point = None
    neg = False
    res = 0
    if string.startswith('-'):
        string = string[1:]
        neg = True
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
        res = res*10 + ord(ch) - ord('0')
    if decimal_point is not None:
        res = res / 10**decimal_point
    return res if not neg else -res
