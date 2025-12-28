import re

def validator_email(email:str) -> bool:
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$'
    if re.match(email_pattern, email):
        return True
    else: return False
def validator_phone(phone:str) -> bool:
    phone_pattern = r'^(?:\+375)\d{9}$'
    if re.match(phone_pattern, phone):
        return True
    else: return False

def validator_password(password:str) -> bool:
    password_pattern = r'^.*(?=.{8,})((?=.*[!@#$%^&*()\-_=+{};:,<.>]){1})(?=.*\d)((?=.*[a-zA-Z]){1}).*$'
    if re.match(password_pattern, password):
        return True
    else: return False

def validator_password_autorithation(password:str) -> bool:
    password_pattern = r'^.{8,}$'
    if re.match(password_pattern, password):
        return True
    else: return False

def validator_date(date) -> bool:
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(date_pattern, str(date)):
        return True
    else: return False

def validator_period(period:str):
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(date_pattern, period):
        return 'date'
    if period.isdigit():
        return 'period'
    return False



