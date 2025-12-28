from functional.func_contracts import dropdown_value, lifetime_constructor, period_dropdown
from utils.buttons_and_inputs import button_state, input_hint, calendar_button
from utils.validator import validator_date
from flet_route import Params, Basket
from utils.style import *
from functional.get_date import load_account
from functional.post_date import post_update_account
from utils.navigation import create_nav
from utils.alter_dialogs import add_invoice, add_cod, save_dialog


class AccountPage:

    def view(self, page: ft.Page, params:Params, basket : Basket):
        page.title = "SupplySystem"
        page.theme_mode = 'light'
        page.fonts = pageFont
        page.window.maximized = True
        page.window.title_bar_hidden = False
        page.window.title_bar_buttons_hidden = False

        document_id = page.client_storage.get('open_element_id')
        document, documents = {}, []

        def page_close_handler(url):
            if disable_column.disabled:
                page.go(url)
            update_contract = read_update()
            if update_contract==document:
                page.go(url)
            else:
                page.open(save_dialog(page, save, update_contract))

        def read_update():
            update_document = document.copy()

            update_document['account_id'] = document_id
            update_document['account'] = document_d.value
            update_document['name'] = supplier_d.value
            update_document['supplier_id'] = supplier_a.value
            update_document['contract_id']=contract_d.key
            update_document['contract'] = contract_d.value
            update_document['open_status'] = status.value
            update_document['account_date'] = document_date_d.value
            update_document['lifetime'] = lifetime_constructor(lifetime_textfield.value, lifetime_dropdown,
                                                               document_date_d.value)
            update_document['payment_type'] = payment_type_input.value
            update_document['payment_date'] = {}
            update_document['delivery_date'] = {}
            for index, x in enumerate(payment.controls):
                update_document['payment_date'][str(index + 1)] = {}
                if x.controls[0].controls[0].value:
                    update_document['payment_date'][str(index + 1)]['close'] = x.controls[0].controls[0].value
                update_document['payment_date'][str(index + 1)]['name'] = x.controls[1].controls[0].value
                if validator_date(x.controls[2].controls[0].value):
                    update_document['payment_date'][str(index + 1)]['date'] = x.controls[2].controls[0].value
                else:
                    update_document['payment_date'][str(index + 1)]['period'] = x.controls[2].controls[0].value
                    update_document['payment_date'][str(index + 1)]['days'] = x.controls[3].controls[0].value
            for index, x in enumerate(delivery.controls):
                update_document['delivery_date'][str(index + 1)] = {}
                if x.controls[0].controls[0].value:
                    update_document['delivery_date'][str(index + 1)]['close'] = x.controls[0].controls[0].value
                update_document['delivery_date'][str(index + 1)]['name'] = x.controls[1].controls[0].value
                if validator_date(x.controls[2].controls[0].value):
                    update_document['delivery_date'][str(index + 1)]['date'] = x.controls[2].controls[0].value
                else:
                    update_document['delivery_date'][str(index + 1)]['period'] = x.controls[2].controls[0].value
                    update_document['delivery_date'][str(index + 1)]['days'] = x.controls[3].controls[0].value
            # update_contract['document'] = document.value
            update_document['description'] = description.value if description.value else None

            return update_document

        def load():
            nonlocal document , documents
            token = page.client_storage.get('access_token')
            document = load_account(token, document_id)
            account_decoration(document)


        def account_decoration(document_):
            print(document_)
            if document_:
                document_d.value=document_['account']
                supplier_d.value=document_.get('name')
                supplier_a.value=document_.get('supplier_id', None)
                contract_d.value=document_.get('contract', None)
                contract_d.key = document_.get('contract_id')
                status.value = document_.get('open_status', None)
                document_date_d.value=document_.get('account_date')
                lifetime_textfield.value = document_.get('lifetime', None)
                description.value = document_.get('description', None)

                if document_['payment_type']:
                    payment_type_input.value=document_['payment_type']
                    payment.controls.clear()
                    if document_['payment_date']:
                        for key, value in document_['payment_date'].items():
                            close = True if 'close' in value else False
                            date_ = value.get('date', None)
                            period_ = value.get('period', None)
                            days = value.get('days', None)
                            payment.controls.append(create_conditions(name=value['name'], close=close, date_=date_,
                                                                      period=period_, days=days))
                    delivery.controls.clear()
                    if document_['delivery_date']:
                        for key, value in document_['delivery_date'].items():
                            close = True if 'close' in value else False
                            date_ = value.get('date', None)
                            period_ = value.get('period', None)
                            days = value.get('days', None)
                            delivery.controls.append(create_conditions(name=value['name'], close=close, date_=date_,
                                                                       period=period_, days=days))
                else:
                    conditions_box.visible = False

        def table_decoration(documents_):
            for x in documents_:
                x.controls.append(create_row(x))

        def save(e, credentials):
            if post_update_account(credentials):
                nonlocal document
                document=credentials
                activate()
                account_decoration(document)
                page.open(ft.SnackBar(ft.Text('Изменение успешно')))

            else: page.open(ft.SnackBar(ft.Text('Ошибка при изменении')))
            page.close(e)

        def save_btn():
            update_document = read_update()
            print(update_document)
            print(document)
            if update_document == document:
                activate()
                account_decoration(update_document)

            else:
                page.open(save_dialog(page, save, update_document))
        def close_btn():
            account_decoration(document)
            page.update()

        def activate():
            nonlocal document
            if document.get('employee_id', None)  == page.client_storage.get('user_id') and page.client_storage.get('user_id') is not None:
                disable_column.disabled=not disable_column.disabled
                disable_column.update()
                for x in [supplier_d,  supplier_a, save_button, cancel_button, activate_button]:
                    x.visible=not x.visible
                    x.update()
            else: page.open(ft.SnackBar(ft.Text('У вас нет доступа к этому счету')))

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
                                  on_click=lambda e: page.open(add_cod(page, document_id, "/document" if type_=='Счёт' else '/specification')),
                                  tooltip="Добавить платежное поручение",
                                  ),
                    ft.IconButton(
                        icon=ft.Icons.INBOX,
                        tooltip="Добавить накладную",
                        on_click=lambda e: page.open(add_invoice(page, document_id, "/document" if type_=='Счёт' else '/specification'))
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

        document_d =  ft.TextField(
            border=ft.InputBorder.UNDERLINE,
            hint_text="Номер счета",
        )
        supplier_d = ft.TextField(
            border=ft.InputBorder.UNDERLINE,
            hint_text="Контрагент",
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
        status = ft.Text()
        contract_d = ft.TextField(
            border=ft.InputBorder.UNDERLINE,
            hint_text="Договор"
        )
        document_date_d = ft.Text()
        date_box = ft.Row(
            controls=[
                document_date_d,
                calendar_button(page, 50, document_date_d)
            ]
        )
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
            status,
            document_d,
            supplier_d,
            supplier_a,
            date_box,
            lifetime_input,
            conditions_box,
            description,
            ft.Row([
                save_button,
                cancel_button
            ])
        ], disabled=True)

        document_action_panel=ft.Column(controls = [
            ft.Row([
                activate_button,
                ft.IconButton(icon=ft.Icons.ATTACH_MONEY_OUTLINED,
                              on_click=lambda e: page.open(add_cod(page, document_id, "/account")),
                              tooltip="Добавить платежное поручение",
                              icon_color=ft.Colors.WHITE,
                              ),
                ft.IconButton(
                    icon=ft.Icons.INBOX,
                    tooltip="Добавить накладную",
                    on_click=lambda e: page.open(add_invoice(page, document_id, "/account")),
                    icon_color=ft.Colors.WHITE,
                ),
            ], alignment=ft.MainAxisAlignment.END),
            disable_column
        ])
        document_child=ft.ListView(controls = [],
                                   spacing=10, padding=20, expand=True, auto_scroll=True,
                                   divider_thickness=1)

        content = ft.ResponsiveRow(
            controls=[
                ft.Column(col=3, controls = [ft.Container(content=document_action_panel,
                                                          expand=True,
                                                          gradient=ft.LinearGradient(  # Градиентный фон
                                                              begin=ft.alignment.center_left,
                                                              end=ft.alignment.center_right,
                                                              colors=[
                                                                  ft.Colors.with_opacity(0.9, '#805a3b'),
                                                                  ft.Colors.with_opacity(0.7, '#805a3b'),
                                                                  ft.Colors.with_opacity(0.9, '#4a3423')
                                                              ]
                                                          ),
                                                          padding=ft.padding.only(left=10, right=10),
                                                          height=800
                                                          )]),
                ft.Column(col=9, controls = [ft.Container(content=document_child)])
            ],
        )

        load()
        return ft.View('/account',
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