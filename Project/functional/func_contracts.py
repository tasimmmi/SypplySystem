import requests, os
from dotenv import load_dotenv
import flet as ft
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from utils.validator import validator_date, validator_period

load_dotenv()
db_url : str = os.getenv('DB_URL')

# dropdown
def dropdown_value(table : str) -> list[ft.dropdown.Option]:
    values = []
    response = requests.get(f'{db_url}/api_user{table}')
    if response.status_code == 200:
        values.append(ft.dropdown.Option(
            key="add_new",
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, size=16, color=ft.Colors.BLUE),
                ft.Text(
                    "Добавить",
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE,
                    size=14
                )
            ], spacing=8)))
        result = response.json()
        for row in result:
            values.append(ft.dropdown.Option(
                key=row['supplier_id'],
                text=row['name']
            ))
    return values

def period_dropdown(function = None, *args) :
    return ft.Dropdown(
        width=100,
        options=[
            ft.dropdown.Option("год"),
            ft.dropdown.Option("месяц"),
            ft.dropdown.Option("день")
        ],
        value="год",  # Значение по умолчанию
        border=ft.InputBorder.NONE,  # Убираем границу для лучшего вида
        content_padding=0,
        on_change= lambda x: function(*args)
    )


def lifetime_constructor(lifetime : str = None,
                         period : str = None,
                         contract_date: str = None):
    if lifetime is None:
        return
    if contract_date == '':
        contract_date = datetime.today().strftime('%Y-%m-%d')

    if validator_date(lifetime) :
        return lifetime

    if isinstance(lifetime, int) or lifetime.isdigit():
        contract_dt = datetime.strptime(contract_date, '%Y-%m-%d').date()
        lifetime_int = int(lifetime)
        match period:
            case 'год':
                result_date = contract_dt + relativedelta(years=lifetime_int)
            case 'месяц' :
                result_date = contract_dt + relativedelta(months=lifetime_int)
            case 'день' :
                result_date = contract_dt + relativedelta(days=lifetime_int)
            case _:
                raise ValueError(f"Неизвестный период: {period}")
        return result_date


def on_change_period(error_output, period :str):
    if validator_period(period) :
        return
    # error_output.value='Не корректный формат: выберите дату или введите плановый срок'
    # error_output.size = 12
    # error_output.update()

def create_dict_textfield(_container, _dict):
    text_box = []
    print(_dict)
    for box in _container.content.controls:
        fi = box.controls[1].controls[0]
        text_box.append(fi)
    for key, value in _dict.items():
        if isinstance(value, dict):
            text_box[int(key)-1].value = value.get('date') if value.get('date') else value.get('period')
    print(text_box)







