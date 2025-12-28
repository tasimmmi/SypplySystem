from utils.style import *
from typing import Callable
import datetime


#buttons
def button_state(text: str,
                 style: dict,
                 width: int,
                 height: int,
                 function: Callable,
                 *args) -> ft.FilledButton:
    return ft.FilledButton(text=text,
                           style=ft.ButtonStyle(**style),
                           width=width,
                           height=height,
                           on_click=lambda e: function(*args)
                           )

def calendar_button(page: ft.Page,
                    width: int,
                    input_field : ft.TextField | ft.Text):
    return ft.IconButton(width=width,
                  icon=ft.Icons.CALENDAR_MONTH,
                  on_click=lambda e: page.open(ft.DatePicker(
                      first_date=datetime.datetime(year=2000, month=1, day=1),
                      last_date=datetime.datetime.now().replace(year=datetime.datetime.now().year + 5).replace(month=12,
                                                                                                               day=31),
                      on_change=lambda e: data_input(e, input_field))))

def data_input(e, input_field):
    setattr(input_field, 'value', e.control.value.strftime('%Y-%m-%d'))
    input_field.update()

#inputs
def input_hint(text: str) -> ft.Container:
    return ft.Container(ft.Text(text), alignment=ft.alignment.center_left, width=230)







