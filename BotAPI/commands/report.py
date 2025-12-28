from utils.refactors import report_refactor

import os, requests
from dotenv import load_dotenv

load_dotenv()
db_url : str = os.getenv('DB_URL')

def report_payments():
    response = requests.get(f'{db_url}/api_telegram/report_payments')
    if response.status_code == 200:
        result = response.json()
        return report_refactor(result)

    return "Ошибка получения данных", None, None

def report_delivery():
    response = requests.get(f'{db_url}/api_telegram/report_delivery')
    if response.status_code == 200:
        result = response.json()
        return report_refactor(result)

    return "Ошибка получения данных", None, None

def report_payments_user(_id):
    response = requests.get(f'{db_url}/api_telegram/report_payments/user/{_id}')
    if response.status_code == 200:
        result = response.json()
        return report_refactor(result)

    return "Ошибка получения данных", None, None

def report_delivery_user(_id):
    response = requests.get(f'{db_url}/api_telegram/report_delivery/user/{_id}')
    if response.status_code == 200:
        result = response.json()
        return report_refactor(result)
    return "Ошибка получения данных", None, None



