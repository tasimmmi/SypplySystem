import requests
import os
import logging
from dotenv import load_dotenv

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

def post_account_to_contract(credentials):
    try:
        response = requests.post(f'{db_url}/api_user/contract/add_account', json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return True if response.status_code == 200 else False
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при добавлении аккаунта: {e}')

def post_specification_to_contract(credentials):
    try:
        response = requests.post(f'{db_url}/api_user/contract/add_specification', json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return True if response.status_code == 200 else False
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при добавлении спецификации: {e}')

def post_cod(credentials):
    try:
        response = requests.post(f'{db_url}/api_user/create_cod', json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return True if response.status_code == 200 else False
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при создании cod: {e}')

def post_invoice(credentials):
    try:
        response = requests.post(f'{db_url}/api_user/create_invoice', json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return True if response.status_code == 200 else False
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при создании invoice: {e}')
        return False

def post_update_contract(credentials):
    print(credentials)
    try:
        response = requests.post(f'{db_url}/api_user/update_contract', json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return True if response.status_code == 200 else False
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при обновлении контракта: {e}')

def post_update_account(credentials):
    print(credentials)
    try:
        response = requests.post(f'{db_url}/api_user/update_account', json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return True if response.status_code == 200 else False
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при обновлении контракта: {e}')

def post_update_specification(credentials):
    print(credentials)
    try:
        response = requests.post(f'{db_url}/api_user/update_specification', json=credentials)
        logger.info(f'Код ответа: {response.status_code}, Ответ: {response.text}')
        return True if response.status_code == 200 else False
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка соединения при обновлении контракта: {e}')
