from flet_route import Params, Basket
from utils.style import *
from utils.filters import AccountSpecifFilter
from functional.get_date import load_accounts_specifications, filter_accounts
from utils.navigation import create_nav


class AccountsPage:

    def view(self, page: ft.Page, params:Params, basket : Basket):
        page.title = "SupplySystem"
        page.theme_mode = 'light'
        page.fonts = pageFont
        page.window.maximized = True
        page.window.title_bar_hidden = False
        page.window.title_bar_buttons_hidden = False

        rows = []

        # functions

        def load():
            nonlocal rows
            token = page.client_storage.get('access_token')
            rows = load_accounts_specifications(token)
            decoration(rows)

        def decoration(rows_):
            content.controls.clear()
            content.controls.append(create_row())
            if rows_:
                for row in rows_:
                    content.controls.append(create_row(row))

        def open_account(account_id_):
            page.client_storage.set('open_element_id', account_id_)
            page.go('/account')

        def open_contract(contract_id_):
            page.client_storage.set('open_element_id', contract_id_)
            page.go('/contract')

        def open_supplier(supplier_id_):
            page.client_storage.set('open_supplier_id', supplier_id_)
            page.go('/supplier')

        def create_row(row: dict = None):
            type_ = ft.Text(row.get("type"), None, **TableTextStyle) if row else ft.Text('Документ', **TableTextHeadersStyle)
            account_ = ft.Text(row.get('account', None), **TableMainInformationStyle) if row else ft.Text('Номер счета', **TableTextHeadersStyle)
            contract_ = ft.GestureDetector(
                content=ft.Text(row.get('contract', None), **TableTextStyle),
                on_tap=lambda e: open_contract(row.get('contract_id'))
            )  \
                if row else ft.Text('Номер договора', **TableTextHeadersStyle)
            date_ = ft.Text(row.get('account_date', None), **TableTextStyle) if row else ft.Text('Дата заключения', **TableTextHeadersStyle)
            supplier_ = ft.GestureDetector(
                content=ft.Text(row.get('name', None), **TableTextStyle),
                on_tap=lambda e: open_supplier(row.get('supplier_id'))
            ) \
                if row else ft.Text('Контрагент', **TableTextHeadersStyle)
            status_ = ft.Text(value=row.get('open_status', None), **TableTextStyle) if row else ft.Text('Статус',
                                                                                      **TableTextHeadersStyle)
            employee_ = ft.Text(row.get('first_name', None), **TableTextStyle) if row else ft.Text('Ведущий специалист',
                                                                                 **TableTextHeadersStyle)
            description_ = ft.Text(row.get('description', None), **TableTextStyle) if row else ft.Text('Описание', **TableTextHeadersStyle)
            return ft.Container(
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(col=1, controls=[type_]),
                        ft.Column(col=2, controls=[account_]),
                        ft.Column(col=2, controls=[contract_]),
                        ft.Column(col=1, controls=[date_]),
                        ft.Column(col=2, controls=[supplier_]),
                        ft.Column(col=1, controls=[status_]),
                        ft.Column(col=1, controls=[employee_]),
                        ft.Column(col=2, controls=[description_])
                    ],
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    columns=12
                ),
                on_click=lambda e: open_account(row.get('account_id')),
                padding=ft.padding.all(10),
                ** TableRowHeadersStyle if not row else TableRowStyle
            )

        def search(pattern: str):
            search_row = [create_row()]
            for row in rows:
                for value in row.values():
                    if isinstance(value, int) or isinstance(value, bool):
                        continue
                    if pattern in value:
                        search_row.append(create_row(row))
                        print(search_row)
                        break
            content.controls = search_row
            content.update()

        def open_close_filters(e):
            filter_column.visible = not filter_column.visible
            page.update()

        def apply_filters_callback(credentials):
            token = page.client_storage.get('token')
            contracts_f = filter_accounts(credentials, token)
            contracts_ = contracts_f
            decoration(contracts_)
            content.update()

        #views

        content = ft.ListView(expand=True,
                              spacing = 1
                              )

        page_name = ft.Container(ft.Text('Договора', **TitleStyle), alignment=ft.alignment.center, margin=20)
        anchor = ft.SearchBar(

            bar_hint_text="Search",
            view_hint_text="Введите данные",
            on_change=lambda e: search(e.control.value),
            on_submit=lambda e: search(e.control.value),
            autofocus=True
        )
        filter_button = ft.IconButton(width=50,
                                      icon=ft.Icons.FILTER_LIST_ALT,
                                      on_click=lambda e: open_close_filters(e))

        load()

        # filters
        filter_data = AccountSpecifFilter(
            page=page,
            function_apply=apply_filters_callback,
            close_function=lambda e: open_close_filters(e)
        )
        filter_column = filter_data.create_filters()

        return ft.View('/accounts',
                   controls=[
                       ft.Stack([
                           ft.Column([
                               create_nav(page, 3),
                               page_name,
                               filter_button,
                               anchor,
                               content
                           ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                           filter_column
                       ]),

                   ],
                   scroll=ft.ScrollMode.AUTO,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   bgcolor=PageBgColor,
                   padding=0
                   )
