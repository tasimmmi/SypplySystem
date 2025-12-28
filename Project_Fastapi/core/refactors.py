from datetime import datetime
import re


def convert_date (date_str: str, direction : bool) -> str:
    print(date_str)
    try:
        if direction:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            return datetime.strftime(date_obj, '%Y-%m-%d')
        else:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return datetime.strftime(date_obj, '%d/%m/%Y')
    except ValueError:
        raise ValueError(f"Некорректный формат даты: {date_str}")

def validator_period(period):
    period = str(period)
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(date_pattern, period):
        return True
    else: return False

