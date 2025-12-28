import os, requests
from dotenv import load_dotenv

from utils.user_constructor import user_construct

load_dotenv()
db_url : str = os.getenv('DB_URL')

def create_employee(new_employee):
    credentials = {
        "t_id" : new_employee.id,
        "first_name" : new_employee.first_name,
        "is_group" : True
    }
    response = requests.post(f'{db_url}/api_telegram/create_employee', json=credentials)
    if response.status_code == 200:
        result = response.json()
        return print(result)
    return print("Unsuccessful")

def start_employee(new_employee):
    credentials, password = user_construct()
    credentials['t_id'] = new_employee.id
    response = requests.post(f'{db_url}/api_telegram/start_employee/{new_employee.id}', json=credentials)
    if response.status_code == 200:
        result = response.json()
        login = result['login'] if 'login' in result else None
        return login, password
    return None, None

def exit_employee(t_id:int):
    response = requests.post(f'{db_url}/api_telegram/exit_employee/{t_id}')
    print(response.json())
