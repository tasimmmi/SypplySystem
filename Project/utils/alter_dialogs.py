import flet as ft
from datetime import date
from utils.buttons_and_inputs import button_state, input_hint, calendar_button
from utils.style import *
from functional.func_contracts import dropdown_value, period_dropdown, lifetime_constructor
from utils.validator import validator_date, validator_period
from functional.post_date import post_account_to_contract, post_specification_to_contract, post_cod, post_invoice, post_update_contract

def clean(fields):
    pass
def dropdown_add_button(e):
    if e.control.value == "add_new":
        print("Открыть форму добавления контрагента")

error_bgcolor = ft.Colors.RED_100
error_text_style = ft.TextStyle(color=ft.Colors.RED_400, size=12)

def create_error_indicator(message: str):
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_400, size=16),
            ft.Text(message, style=error_text_style)
        ]),
        animate_opacity=300,
        opacity=1 if message else 0
    )


def add_to_contract(page: ft.Page, contract_id: int):

    def add():
        credentials = {
            'item' : number_input.value,
            'contract_id' : contract_id,
            'document_date' : contract_date_text.value,
            'lifetime' : str(lifetime_constructor(lifetime_textfield.value, lifetime_dropdown.value, contract_date_text.value)),
            'payment_type' : payment_type_input.value,
            'employee_id' : page.client_storage.get('user_id')
        }
        if description.value:
            credentials['description'] = description.value
        for key, box in enumerate(payment_conditions):
            value = box.controls[1].controls[0].value
            if validator_date(value):
                credentials[f'payment{key + 1}'] = value
            else:
                credentials[f'payment{key + 1}'] = value
                credentials[f'payment{key + 1}_type'] = box.controls[2].controls[0].value
        for key, box in enumerate(delivery_conditions):
            value = box.controls[1].controls[0].value
            if validator_date(value):
                credentials[f'delivery'] = value
            else:
                credentials[f'delivery'] = value
                credentials[f'delivery_type'] = box.controls[2].controls[0].value
        success = post_account_to_contract(credentials) if type_dropdown.value == 'Счёт' else post_specification_to_contract(credentials)
        if success:
            page.close(dlg)
            page.update()
        else : ft.SnackBar(ft.Text('Ошибка добавления'))
    #
    def create_conditions(name: str, calendar_visible: bool = True):
        name = ft.Text(name)
        date_field = ft.TextField(label='Дата/Срок', tooltip="Введите дату или допустимый срок", **InputWebFieldStyle)
        days = ft.Dropdown(options=[
            ft.dropdown.Option("р.д."),
            ft.dropdown.Option("к.д."),
        ],
            value="к.д.",
            border=ft.InputBorder.NONE,
            content_padding=0)
        calendar = calendar_button(page, 50, date_field)
        calendar.visible = calendar_visible
        return ft.ResponsiveRow(controls=[
            ft.Column(col=3, controls=[name]),
            ft.Column(col=4, controls=[date_field]),
            ft.Column(col=3, controls=[days]),
            ft.Column(col=2, controls=[calendar])
        ], expand=True, columns=12, spacing=2)

    payment_conditions = []
    delivery_conditions = []

    def payment_type_choosing(_type):
        payment_terms_container.controls.clear()
        delivery_terms_container.controls.clear()
        match (_type):
            case 'Частичная предоплата + оплата перед поставкой' | 'Частичная предоплата + оплата после поставки':
                payment_array = {'Предоплата': True, 'Остаток': False}
                delivery_array = {'Поставка': False}
            case 'Предоплата 100%':
                payment_array = {'Предоплата': True}
                delivery_array = {'Поставка': False}
            case 'После поставки':
                payment_array = {'Оплата': False}
                delivery_array = {'Поставка': True}
            case _:
                payment_array = []
                delivery_array = []
        for key, value in payment_array.items():
            payment_conditions.append(create_conditions(key, value))
        for key, value in delivery_array.items():
            delivery_conditions.append(create_conditions(key, value))
        payment_terms_container.controls = payment_conditions
        delivery_terms_container.controls = delivery_conditions
        page.update()

    # Стили для акцентного выделения ошибок

    def check_inputs():
        message = ''
        error_fields = []

        # Проверка номер договора
        if not number_input.value:
            error_fields.append(number_input)
            if not message:
                message = 'Не все поля заполнены'


        try:
            contract_date = date.fromisoformat(contract_date_text.value)
            if contract_date > date.today():
                error_fields.append(contract_date_text)
                if not message:
                    message = 'Неверное значение даты'
        except ValueError:
            error_fields.append(contract_date_text)
            if not message:
                message = 'Неверный формат даты'

    # Проверка срока действия
        if not validator_period(lifetime_textfield.value):
            error_fields.append(lifetime_textfield)
            if not message:
                message = 'Срок действия должен быть датой или кол-вом дней'

        # Проверка типа оплаты
        if not payment_type_input.value:
            error_fields.append(payment_type_input)
            if not message:
                message = 'Укажите тип оплаты'

        # Проверка сроков оплаты (если выбран тип оплаты)
        if payment_type_input.value:
            for i, x in enumerate(payment_conditions):
                if not validator_period(x.controls[1].controls[0].value):
                    error_fields.append(x.controls[1].controls[0])
                    if not message:
                        message = 'Заполните сроки оплаты'
                    break
                elif validator_date(x.controls[1].controls[0].value):
                    if date.fromisoformat(x.controls[1].controls[0].value) < date.fromisoformat(
                            contract_date_text.value):
                        error_fields.append(x.controls[1].controls[0])
                        if not message:
                            message = 'Неверное значение даты в сроках оплаты'
                        break


        for i, x in enumerate(delivery_conditions):
            if not validator_period(x.controls[1].controls[0].value):
                error_fields.append(x.controls[1].controls[0])
                if not message:
                    message = 'Заполните сроки поставки'
                break
            elif validator_date(x.controls[1].controls[0].value):
                if date.fromisoformat(x.controls[1].controls[0].value) < date.fromisoformat(
                        contract_date_text.value):
                    error_fields.append(x.controls[1].controls[0])
                    if not message:
                        message = 'Неверное значение даты в сроках поставки'
                    break

    # Проверка даты окончания действия договора
        try:
            end_date = lifetime_constructor(lifetime_textfield.value, lifetime_dropdown.value,
                                            contract_date_text.value)
            if end_date < date.fromisoformat(contract_date_text.value):
                error_fields.append(lifetime_textfield)
                if not message:
                    message = 'Дата окончания не может быть раньше даты заключения'
        except:
            pass

        # Создаем список всех полей для сброса стилей
        all_fields = [number_input, lifetime_textfield, payment_type_input]

        # Добавляем все поля сроков оплаты и поставки
        for x in payment_conditions:
            all_fields.append(x.controls[1].controls[0])
        for x in delivery_conditions:
            all_fields.append(x.controls[1].controls[0])

        # Сброс выделения ошибок - возвращаем стандартный фон
        for field in all_fields:
            if hasattr(field, 'bgcolor'):
                field.bgcolor = ft.Colors.WHITE
                field.update()
            if hasattr(field, 'fill_color'):
                field.fill_color = ft.Colors.WHITE
                field.update()
            print(field)

        # Подсветка полей с ошибками - устанавливаем красный фон
        for field in error_fields:
            if hasattr(field, 'bgcolor'):
                field.bgcolor = ft.Colors.RED_100
                field.update()
            if hasattr(field, 'fill_color'):
                field.fill_color = ft.Colors.RED_100
                field.update()
            print(field)


        # Обновление индикатора ошибки
        if message:
            error_indicator.content.controls[1].value = message
            error_indicator.opacity = 1
            error_indicator.update()
        else:
            error_indicator.opacity = 0
            error_indicator.update()
            add()

    # Основной код диалога
    type_dropdown = ft.Dropdown(
        editable=True,
        width=350,
        options=[
            ft.dropdown.Option('Счёт'),
            ft.dropdown.Option('Спецификация')
        ],
        value='Счёт',
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        border_radius=8
    )

    add_button = button_state('Добавить договор', ButtonBlueStyle, 360, 50, check_inputs)

    number_hint = input_hint('Номер договора')
    number_input = ft.TextField(**InputWebFieldStyle)

    contract_date_hint = input_hint('Дата заключения')
    contract_date_text = ft.Text(str(date.today()), width=310)
    contract_date_input = ft.Row([
        contract_date_text,
        calendar_button(page, 50, contract_date_text)
    ])

    lifetime_hint = input_hint('Действителен до (в течение)')
    lifetime_textfield = ft.TextField(label="Дата/Срок", width=200)
    lifetime_dropdown = period_dropdown()
    lifetime_input = ft.Column([
        lifetime_hint,
        ft.Row([
            lifetime_textfield,
            lifetime_dropdown,
            calendar_button(page, 50, lifetime_textfield)
        ]),
    ])

    document_box = ft.Container(
        content=ft.Row([
            ft.Text(value='', width=250),
            ft.IconButton(
                width=100,
                icon=ft.Icons.FILE_DOWNLOAD_OUTLINED,
                icon_color=ft.Colors.BLUE_400
            )
        ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        border_radius=8,
        border=ft.border.all(1, ft.Colors.GREY_300),
        padding=ft.padding.symmetric(horizontal=10, vertical=8)
    )

    payment_terms_container = ft.Column(controls=[])
    delivery_terms_container = ft.Column(controls=[])

    payment_type_input = ft.Dropdown(
        editable=True,
        width=350,
        options=[
            ft.dropdown.Option('Предоплата 100%'),
            ft.dropdown.Option('После поставки'),
            ft.dropdown.Option('Частичная предоплата + оплата перед поставкой'),
            ft.dropdown.Option('Частичная предоплата + оплата после поставки')
        ],
        label='Тип оплаты',
        content_padding=ft.padding.symmetric(horizontal=10, vertical=8),
        border_radius=8,
        on_change=lambda e: payment_type_choosing(e.control.value),
        filled=True
    )

    content_container = ft.Container(
        content=ft.Column([
            payment_type_input,
            ft.Divider(height=1),
            ft.Text("Сроки оплаты:", weight=ft.FontWeight.BOLD, size=16),
            payment_terms_container,
            ft.Divider(height=1),
            ft.Text("Сроки поставки:", weight=ft.FontWeight.BOLD, size=16),
            delivery_terms_container,
            ft.Divider(height=1),
        ]),
        padding=ft.padding.only(top=10)
    )

    description = ft.TextField(
        label="Описание",
        multiline=True,
        min_lines=1,
        max_lines=3,
        content_padding=ft.padding.symmetric(horizontal=10, vertical=12),
        **InputWebFieldStyle
    )

    # Индикатор ошибки с анимацией
    error_indicator = create_error_indicator('')

    params_scroll = ft.Container(
        content=ft.Column(
            controls=[
                type_dropdown,
                ft.Container(number_hint, padding=ft.padding.only(top=10)),
                number_input,
                ft.Container(contract_date_hint, padding=ft.padding.only(top=10)),
                contract_date_input,
                lifetime_input,
                content_container,
                description,
                document_box,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=8
        ),
        height=560,
        #padding=ft.padding.symmetric(horizontal=15)
    )

    add_column = ft.Column([
        error_indicator,
        params_scroll,

        ft.Container(add_button, padding=ft.padding.only(top=15))
    ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Вертикальное выравнивание
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    dlg = ft.AlertDialog(
        title=ft.Text("Добавить", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        content=add_column,
        alignment=ft.alignment.center,
        title_padding=ft.padding.all(20),
        content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
        shape=ft.RoundedRectangleBorder(radius=12)
    )
    return dlg

def add_cod(page: ft.Page, id_: int, path : str, contract_id : int = None, ) -> list:

    def save():
        credentials = {
            'item': item_input.value,
            'date': date_text.value
        }
        if contract_id is not None:
            credentials['contract_id'] = contract_id
        if path == '/contract':
            credentials['contract_id'] = id_
        elif path == '/account':
            credentials['account_id'] = id_
        elif path == '/specification':
            credentials['specification_id'] = id_
        else:
            error_indicator.content.controls[1].value = 'Ошибка добавления платежного поручения'
            error_indicator.opacity = 1
            error_indicator.update()
            return
        succes = post_cod(credentials)
        if succes:
            page.open(ft.SnackBar(ft.Text('Успешно')))
            page.close(dlg)
        else:
            page.open(ft.SnackBar(ft.Text('Ошибка создания')))
            page.close(dlg)

    def check_input():
        message = ''
        error_fields = []

        # Проверка номер договора
        if not item_input.value:
            error_fields.append(item_input)
            if not message:
                message = 'Не все поля заполнены'
        try:
            contract_date = date.fromisoformat(date_text.value)
            if contract_date > date.today():
                error_fields.append(date_text)
                if not message:
                    message = 'Неверное значение даты'
        except ValueError:
            error_fields.append(date_text)
            if not message:
                message = 'Неверный формат даты'

        for field in [date_text, error_indicator]:
            if hasattr(field, 'bgcolor'):
                field.bgcolor = ft.Colors.WHITE
                field.update()

        for field in error_fields:
            if hasattr(field, 'bgcolor'):
                field.bgcolor = ft.Colors.RED_100
                field.update()

        if message:
            error_indicator.content.controls[1].value = message
            error_indicator.opacity = 1
            error_indicator.update()
        else:
            error_indicator.opacity = 0
            error_indicator.update()
            save()

    item_hint = input_hint('Номер')
    item_input = ft.TextField(**InputWebFieldStyle)
    date_hint = input_hint('Дата оплаты')
    date_text = ft.Text(str(date.today()), width=310)
    date_input = ft.Row([
        date_text,
        calendar_button(page, 50, date_text)
    ])
    error_indicator = create_error_indicator('')

    column = ft.Column([
        error_indicator,
        item_hint,
        item_input,
        date_hint,
        date_input,
        button_state('Сохранить',
                     ButtonBlueStyle,
                     300, 50,
                    check_input)
    ])
    dlg =ft.AlertDialog(
        title=ft.Text('Платежное поручение', size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        content=ft.Container(
            content=column,
            height=250,  # Фиксированная ширина
            padding=10
        ),
        alignment=ft.alignment.center,
        # title_padding = ft.padding.all(20),
        content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
        shape=ft.RoundedRectangleBorder(radius=12),
        on_dismiss=lambda e: clean(fields=[
            item_input,
            date_input,
        ])
    )
    return dlg

def add_invoice(page: ft.Page, id_: int, path : str, contract_id : int = None):

    def save():
        credentials = {
            'item': item_input.value,
            'date': date_text.value
        }
        if contract_id is not None:
            credentials['contract_id'] = contract_id
        if path == '/contract':
            credentials['contract_id'] = id_
        elif path == '/account':
            credentials['account_id'] = id_
        elif path == '/specification':
            credentials['specification_id'] = id_
        else:
            error_indicator.content.controls[1].value = 'Ошибка добавления платежного поручения'
            error_indicator.opacity = 1
            error_indicator.update()
            return
        succes = post_invoice(credentials)
        if succes:
            page.open(ft.SnackBar(ft.Text('Успешно')))
            page.close(dlg)
        else:
            page.open(ft.SnackBar(ft.Text('Ошибка создания')))
            page.close(dlg)


    def check_input():
        message = ''
        error_fields = []

        # Проверка номер договора
        if not item_input.value:
            error_fields.append(item_input)
            if not message:
                message = 'Не все поля заполнены'
        try:
            contract_date = date.fromisoformat(date_text.value)
            if contract_date > date.today():
                error_fields.append(date_text)
                if not message:
                    message = 'Неверное значение даты'
        except ValueError:
            error_fields.append(date_text)
            if not message:
                message = 'Неверный формат даты'

        for field in [date_text, error_indicator]:
            if hasattr(field, 'bgcolor'):
                field.bgcolor = ft.Colors.TRANSPARENT
                field.update()

        for field in error_fields:
            if hasattr(field, 'bgcolor'):
                field.bgcolor = ft.Colors.RED_100
                field.update()

        if message:
            error_indicator.content.controls[1].value = message
            error_indicator.opacity = 1
            error_indicator.update()
        else:
            error_indicator.opacity = 0
            error_indicator.update()
            save()

    item_hint = input_hint('Номер')
    item_input = ft.TextField(**InputWebFieldStyle)
    date_hint = input_hint('Дата оплаты')
    date_text = ft.Text(str(date.today()), width=310)
    date_input = ft.Row([
        date_text,
        calendar_button(page, 50, date_text)
    ])
    error_indicator = create_error_indicator('')

    column = ft.Column([
        error_indicator,
        item_hint,
        item_input,
        date_hint,
        date_input,
        button_state('Сохранить',
                     ButtonBlueStyle,
                     300, 50,
                    check_input)
    ])
    dlg = ft.AlertDialog(
        title = ft.Text('Накладная', size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        content = ft.Container(
            content=column,
            height=250,  # Фиксированная ширина
            padding=10
        ),
        alignment = ft.alignment.center,
        #title_padding = ft.padding.all(20),
        content_padding = ft.padding.symmetric(horizontal=20, vertical=10),
        shape = ft.RoundedRectangleBorder(radius=12),
        on_dismiss = lambda e: clean(fields=[
            item_input,
            date_input,
        ])
    )
    return dlg


def save_dialog(page: ft.Page, function, credentials):
    dlg= ft.AlertDialog(
        modal=True,
        title=ft.Text("Подтверждение"),
        content=ft.Text("Выхотите сохранить изменения"),
        actions=[
            ft.TextButton("Да", on_click=lambda e: function(dlg, credentials)),
            ft.TextButton("Нет", on_click=lambda e: page.close(dlg)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Modal dialog dismissed!"),
    )
    return dlg







