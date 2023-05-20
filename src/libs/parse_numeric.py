def parse_numeric(numeric):
    if not numeric:
        return None
    if isinstance(numeric, float) or isinstance(numeric, int):
        return float(numeric)
    numeric = numeric.strip()
    try:
        parsed_value = float(numeric)
    except:
        parsed_value = None
    return parsed_value

