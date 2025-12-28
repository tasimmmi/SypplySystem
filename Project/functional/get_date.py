import requests
import os
import logging
from dotenv import load_dotenv

from functional.refactor import status_date_refactor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_requests.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
db_url: str = os.getenv('DB_URL')

# pages load

def load_main_page():
    try:
        response = requests.get(f'{db_url}/api_user/main')
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        if response.status_code == 200:
            data = response.json()
            suppliers = data.get("suppliers", [])
            contracts = data.get("contracts", [])
            accounts = data.get("accounts", [])
            specifications = data.get("specifications", [])
            accounts = status_date_refactor(accounts, 'date')
            specifications = status_date_refactor(specifications, 'date')
            return suppliers, contracts, accounts, specifications
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при получении данных главной страницы: {e}')
    return [], [], [], []

def load_contract(token, _id : int):
    try:
        response = requests.get(f'{db_url}/api_user/get_contract/{_id}', headers={'Authorization': f'Bearer {token}'})
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        if response.status_code == 200:
            data = response.json()
            contract = data.get("contract")
            documents = data.get("documents")
            return contract, documents
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при считывании договора: {e}')
    return {}, []

def load_contracts(token):
    try:
        response = requests.get(f'{db_url}/api_user/get_contracts', headers={'Authorization': f'Bearer {token}'})
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при получении договоров: {e}')
    return []

def load_accounts_specifications(token):
    try:
        response = requests.get(f'{db_url}/api_user/get_accounts_specifications', headers={'Authorization': f'Bearer {token}'})
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при получении счетов: {e}')
    return []

def load_suppliers(token):
    try:
        response = requests.get(f'{db_url}/api_user/get_suppliers', headers={'Authorization': f'Bearer {token}'})
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при получении контрагентов: {e}')
    return []

def suppliers_name():
    try:
        response = requests.get(f'{db_url}/api_user/suppliers_names')
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при получении контрагентов: {e}')
    return []

def load_account(token, _id : int):
    try:
        response = requests.get(f'{db_url}/api_user/get_account/{_id}', headers={'Authorization': f'Bearer {token}'})
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return  response.json() if response.status_code == 200 else {}
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при считывании счета: {e}')
    return []



### FILTERS QUERY

def filter_main_page(credentials, token):
    try :
        response = requests.post(f'{db_url}/api_user/filter_main', headers={'Authorization': f'Bearer {token}'}, json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        if response.status_code == 200:
            data = response.json()
            suppliers = data.get("suppliers", [])
            contracts = data.get("contracts", [])
            accounts = data.get("accounts", [])
            specifications = data.get("specifications", [])
            accounts = status_date_refactor(accounts, 'date')
            specifications = status_date_refactor(specifications, 'date')
            return suppliers, contracts, accounts, specifications
        return [], [], [], []
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при загрузки главной страницый: {e}')
    return [], [], [], []

def filter_contracts(credentials, token):
    try :
        response = requests.post(f'{db_url}/api_user/filter_contracts', headers={'Authorization': f'Bearer {token}'}, json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при считывании договоров: {e}')
    return []

def filter_accounts(credentials, token):
    try :
        response = requests.post(f'{db_url}/api_user/filter_accounts', headers={'Authorization': f'Bearer {token}'}, json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при считывании счетов и спецификаций: {e}')
    return []


