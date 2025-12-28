from functional.func_contracts import dropdown_value, lifetime_constructor, period_dropdown
from utils.buttons_and_inputs import button_state, input_hint, calendar_button
from utils.validator import validator_date
from flet_route import Params, Basket
from utils.style import *
from functional.get_date import load_contract
from functional.post_date import post_update_contract
from utils.navigation import create_nav
from utils.alter_dialogs import add_to_contract, add_invoice, add_cod, save_dialog


class ContractPage:

    def view(self, page: ft.Page, params:Params, basket : Basket):
        page.title = "SupplySystem"
        page.theme_mode = 'light'
        page.fonts = pageFont
        page.window.maximized = True
        page.window.title_bar_hidden = False
        page.window.title_bar_buttons_hidden = False

        contact_id = page.client_storage.get('open_element_id')
        contract, documents = {}, []

        def page_close_handler(url):
            if disable_column.disabled:
                page.go(url)
            update_contract = read_update()
            if update_contract==contract:
                page.go(url)
            else:
                page.open(save_dialog(page, save, update_contract))

        def read_update():
            update_contract = contract.copy()

            update_contract['contract_id'] = contact_id
            update_contract['contract'] = contract_d.value
            update_contract['name'] = supplier_d.value
            update_contract['supplier_id'] = supplier_a.value
            update_contract['contract_date'] = contract_date_d.value
            update_contract[
                'contract_type'] = 'До выполнения обязательств' if contract_type_d.value else 'До истечения срока'
            update_contract['lifetime'] = lifetime_constructor(lifetime_textfield.value, lifetime_dropdown,
                                                               contract_date_d.value) if not contract_type_d.value else None
            update_contract['payment_type'] = payment_type_input.value
            update_contract['payment_date'] = {}
            update_contract['delivery_date'] = {}
            for index, x in enumerate(payment.controls):
                update_contract['payment_date'][str(index+1)] = {}
                if x.controls[0].controls[0].value:
                    update_contract['payment_date'][str(index+1)]['close'] = x.controls[0].controls[0].value
                update_contract['payment_date'][str(index+1)]['name'] = x.controls[1].controls[0].value
                if validator_date(x.controls[2].controls[0].value):
                    update_contract['payment_date'][str(index+1)]['date'] = x.controls[2].controls[0].value
                else:
                    update_contract['payment_date'][str(index+1)]['period'] = x.controls[2].controls[0].value
                    update_contract['payment_date'][str(index+1)]['days'] = x.controls[3].controls[0].value
            for index, x in enumerate(delivery.controls):
                update_contract['delivery_date'][str(index + 1)] = {}
                if x.controls[0].controls[0].value:
                    update_contract['delivery_date'][str(index+1)]['close'] = x.controls[0].controls[0].value
                update_contract['delivery_date'][str(index+1)]['name'] = x.controls[1].controls[0].value
                if validator_date(x.controls[2].controls[0].value):
                    update_contract['delivery_date'][str(index+1)]['date'] = x.controls[2].controls[0].value
                else:
                    update_contract['delivery_date'][str(index+1)]['period'] = x.controls[2].controls[0].value
                    update_contract['delivery_date'][str(index+1)]['days'] = x.controls[3].controls[0].value
            # update_contract['document'] = document.value
            update_contract['description'] = description.value if description.value else None

            return update_contract

        def load():
            nonlocal contract , documents
            token = page.client_storage.get('access_token')
            contract, documents = load_contract(token, contact_id)
            contract_decoration(contract)
            table_decoration(documents)

        def contract_decoration(contract_):
            contract_d.value=contract_['contract']
            supplier_d.value=contract_.get('name')
            supplier_a.value=contract_.get('supplier_id')
            contract_date_d.value=contract_.get('contract_date')
            contract_type_d.value= False if contract_.get('lifetime', None) else True
            lifetime_input.visible= not contract_type_d.value
            lifetime_textfield.value = contract_.get('lifetime', None)
            description.value = contract_.get('description', None)

            if contract_['payment_type']:
                payment_type_input.value=contract_['payment_type']
                payment.controls.clear()
                if contract_['payment_date']:
                    for key, value in contract_['payment_date'].items():
                        close = True if 'close' in value else False
                        date_ = value.get('date', None)
                        period_ = value.get('period', None)
                        days = value.get('days', None)
                        payment.controls.append(create_conditions( name=value['name'], close=close, date_=date_,
                                                                    period=period_, days=days))
                delivery.controls.clear()
                if contract_['delivery_date']:
                    for key, value in contract_['delivery_date'].items():
                        close = True if 'close' in value else False
                        date_ = value.get('date', None)
                        period_ = value.get('period', None)
                        days = value.get('days', None)
                        delivery.controls.append(create_conditions( name=value['name'], close=close, date_=date_,
                                                                    period=period_, days=days))
            else:
                conditions_box.visible = False

        def table_decoration(documents_):
            for x in documents_:
                contract_child.controls.append(create_row(x))

        def save(e, credentials):
            if post_update_contract(credentials):
                nonlocal contract
                contract=credentials
                activate()
                contract_decoration(contract)
                page.open(ft.SnackBar(ft.Text('Изменение успешно')))

            else: page.open(ft.SnackBar(ft.Text('Ошибка при изменении')))
            page.close(e)

        def save_btn():
            update_contract = read_update()
            print(update_contract)
            print(contract)
            if update_contract == contract:
                activate()
                # contract_decoration(update_contract)
            else:
                page.open(save_dialog(page, save, update_contract))

        def close_btn():
            contract_decoration(contract)
            page.update()

        def close_cod_invoice(dlg):
            if dlg.open:
                page.close(dlg)
            else: page.open(dlg)


        def activate():
            nonlocal contract
            if contract['employee_id']  == page.client_storage.get('user_id'):
                disable_column.disabled=not disable_column.disabled
                disable_column.update()
                for x in [supplier_d,  supplier_a, save_button, cancel_button, activate_button]:
                    x.visible=not x.visible
                    x.update()
            else: page.open(ft.SnackBar(ft.Text('У вас нет доступа к этому договору')))

        def check_box_handler(e):
            lifetime_input.visible= not lifetime_input.visible
            lifetime_input.update()


        def create_row(document_dict : dict):
            type_=document_dict['document_type']
            row = ft.ResponsiveRow(controls=[
                ft.Column(col=2, controls=[ft.Text(type_)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column(col=1, controls=[ft.Text(document_dict['document'])],  alignment=ft.MainAxisAlignment.CENTER),
                ft.Column(col=1, controls=[ft.Text(document_dict['open_status'])], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column(col=2, controls=[ft.Text(document_dict['status_date'])], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column(col=1, controls=[ft.Text(document_dict['first_name'])], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column(col=3, controls=[ft.Text(document_dict['description'])], alignment=ft.MainAxisAlignment.CENTER),
                ft.Column(col=2, controls=[ft.Row([
                    ft.IconButton(icon=ft.Icons.ATTACH_MONEY_OUTLINED,
                                  on_click=lambda e: page.open(add_cod(page, contact_id, "/account" if type_=='Счёт' else '/specification')),
                                  tooltip="Добавить платежное поручение",
                                  ),
                    ft.IconButton(
                        icon=ft.Icons.INBOX,
                        tooltip="Добавить накладную",  # Добавьте эту строку
                        on_click=lambda e: page.open(add_invoice(page, contact_id, "/account" if type_=='Счёт' else '/specification'))
                    ),
                    ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE,
                                  on_click=lambda e: print('Add cod'),
                                  tooltip="Просмотреть"
                                  )
                ])])
            ],alignment=ft.MainAxisAlignment.CENTER)
            return ft.Container(content=row,
                                on_click=lambda e: print('Read document'))

        def create_conditions(name:str, close:bool = False,
                              calendar_exist: bool=True,
                              date_ : str = None,
                              period: str = None,
                              days: str ='р.д.'):
            close=ft.Checkbox(value=close,disabled=True)
            name = ft.Text(name)
            date_field = ft.TextField(value=date_ if date_ else period, border=ft.InputBorder.UNDERLINE,)
            days = ft.Dropdown(options=[
                    ft.dropdown.Option("р.д."),
                    ft.dropdown.Option("к.д."),
                ],
                value=days,
                border=ft.InputBorder.NONE,
                content_padding=0)
            calendar = calendar_button(page, 50, date_field)
            return ft.ResponsiveRow(controls=[
                ft.Column(col=1, controls=[close]),
                ft.Column(col=3, controls=[name]),
                ft.Column(col=3, controls=[date_field]),
                ft.Column(col=3, controls=[days]),
                ft.Column(col=2, controls=[calendar if calendar_exist else ft.Text()])
            ], expand=True, columns=12, spacing=2)

        payment_conditions = []
        delivery_conditions = []
        def payment_type_choosing(_type):
            payment.controls.clear()
            delivery.controls.clear()
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
                    payment_array = {}
                    delivery_array = {}
            for key, value in payment_array.items():
                payment_conditions.append(create_conditions(key, calendar_exist=value))
            for key, value in delivery_array.items():
                delivery_conditions.append(create_conditions(key, calendar_exist=value))
            payment.controls = payment_conditions
            delivery.controls = delivery_conditions
            page.update()

        activate_button = ft.IconButton(
            icon=ft.Icons.REMOVE_RED_EYE,
            on_click=lambda e: activate(),
            icon_color=ft.Colors.WHITE,
        )

        contract_d =  ft.TextField(
            border=ft.InputBorder.UNDERLINE,
            hint_text="Номер контракта",
        )
        supplier_d = ft.TextField(
            border=ft.InputBorder.UNDERLINE,
            hint_text="Контракт",
        )
        supplier_a = ft.Dropdown(
            editable=True,
            hint_text="Выберите контрагента",
            options=dropdown_value('/suppliers_names'),
            enable_filter=True,
            on_change=lambda e: setattr(supplier_d, 'value', e.control.value),
            width=400,
            visible=False
        )
        contract_date_d = ft.TextField(
            border=ft.InputBorder.UNDERLINE,
            hint_text="Дата заключения"
        )
        contract_type_d = ft.Checkbox(label = 'До выполнения обязательств', value=False, on_change=lambda e: check_box_handler(e))

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

        payment_type_input = ft.Dropdown(
            editable=True,
            width=350,
            options=[
                ft.dropdown.Option(key='Предоплата 100%'),
                ft.dropdown.Option(key='После поставки'),
                ft.dropdown.Option(key='Частичная предоплата + оплата перед поставкой'),
                ft.dropdown.Option(key='Частичная предоплата + оплата после поставки')
            ],
            hint_text='Тип оплаты',
            content_padding=0,
            on_change=lambda e: payment_type_choosing(e.control.value)
        )


        payment = ft.ExpansionTile(
                title= ft.Text(f'Оплата',
                               overflow=ft.TextOverflow.ELLIPSIS,
                               text_align=ft.TextAlign.LEFT
                               ),
                initially_expanded=True,
                tile_padding = ft.padding.only(left=10),
                shape=ft.RoundedRectangleBorder(radius=5),
                #disabled=True,
            )
        delivery = ft.ExpansionTile(
            title=ft.Text(f'Поставка',
                          overflow=ft.TextOverflow.ELLIPSIS,
                          expand=True,
                          text_align=ft.TextAlign.LEFT
                          ),
            initially_expanded=True,
            tile_padding=ft.padding.only(left=10),
            shape=ft.RoundedRectangleBorder(radius=5),
            #disabled=True
        )

        conditions_box = ft.Column([
            payment_type_input,
            payment,
            delivery
        ])
        description = ft.TextField(
            label="Описание",
            multiline=True,
            min_lines=1,
            max_lines=3,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=12),
            **InputWebFieldStyle
        )

        cancel_button =  button_state('Отменить',
                                      ButtonWhiteStyle,
                                      100, 50,
                                      close_btn)
        cancel_button.visible=False

        save_button = button_state('Сохранить',
                             ButtonBlueStyle,
                             100, 50,
                             save_btn)
        save_button.visible=False

        disable_column=ft.Column([
            contract_d,
            supplier_d,
            supplier_a,
            contract_date_d,
            contract_type_d,
            lifetime_input,
            conditions_box,
            description,
            ft.Row([
                save_button,
                cancel_button
            ])
        ], disabled=True)

        contract_info=ft.Column(controls = [
            ft.Row([
                activate_button,
                ft.IconButton(icon=ft.Icons.ADD,
                              on_click=lambda e: page.open(add_to_contract(page, contact_id, 6)),
                              tooltip="Добавить счёт/спецификацию",
                              icon_color=ft.Colors.WHITE,
                              ),
                ft.IconButton(icon=ft.Icons.ATTACH_MONEY_OUTLINED,
                              on_click=lambda e: page.open(add_cod(page, contact_id, "/contract", closeclose_cod_invoice(e.control))),
                              tooltip="Добавить платежное поручение",
                              icon_color=ft.Colors.WHITE,
                              ),
                ft.IconButton(
                    icon=ft.Icons.INBOX,
                    tooltip="Добавить накладную",
                    on_click=lambda e: page.open(add_invoice(page, contact_id, "/contract")),
                    icon_color=ft.Colors.WHITE,
                ),
            ], alignment=ft.MainAxisAlignment.END),
            disable_column
        ])
        contract_child=ft.ListView(controls = [],
                                   spacing=10, padding=20, expand=True, auto_scroll=True,
                                   divider_thickness=1)

        content = ft.ResponsiveRow(
            controls=[
                ft.Column(col=3, controls = [ft.Container(content=contract_info,
                                                          expand=True,
                                                          gradient=ft.LinearGradient(  # Градиентный фон
                                                              begin=ft.alignment.center_left,
                                                              end=ft.alignment.center_right,
                                                              colors=[
                                                                  ft.Colors.with_opacity(0.9, '#805a3b'),
                                                                  # Полупрозрачный синий
                                                                  ft.Colors.with_opacity(0.7, '#805a3b'),
                                                                  # Более прозрачный синий
                                                                  ft.Colors.with_opacity(0.9, '#4a3423'),
                                                                  # Еще более прозрачный
                                                              ]
                                                          ),
                                                          padding=ft.padding.only(left=10, right=10),
                                                          height=800
                                                          )]),
                ft.Column(col=9, controls = [ft.Container(content=contract_child)])
            ],
        )

        load()
        return ft.View('/contract',
                       controls=[
                           ft.Stack([
                               ft.Column([
                                   create_nav(page, 0, page_close_handler),
                                   content
                               ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                           ])
                       ],
                       scroll=ft.ScrollMode.AUTO,
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                       bgcolor=PageBgColor,
                       padding=0
                       )