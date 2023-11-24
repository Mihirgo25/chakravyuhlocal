from datetime import datetime
import dateutil.parser as parser

def convert_date_format(date, dayfirst=True):
    if not date:
        return date
    parsed_date = parser.parse(date, dayfirst=dayfirst)
    return datetime.strptime(str(parsed_date.date()), "%Y-%m-%d")