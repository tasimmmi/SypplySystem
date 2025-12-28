from flet_route import Params, Basket
from utils.filters import FilterData
from functional.get_date import load_main_page, filter_main_page
from utils.navigation import create_nav
from utils.schems import Supplier,Contract,Account,Specification
from utils.style import *



class MainPage:

    def view(self, page: ft.Page, params:Params, basket : Basket):
        page.title = "SupplySystem"
        page.theme_mode = 'light'
        page.fonts = pageFont
        page.window.maximized = True
        page.window.title_bar_hidden = False
        page.window.title_bar_buttons_hidden = False

        suppliers, contracts, accounts, specifications = [], [], [], []
        suppliers_list = []

        # Создание экземпляра

        # functions

        def load():
            nonlocal suppliers, contracts, accounts, specifications
            suppliers, contracts, accounts, specifications = load_main_page()
            cardmaker(suppliers, contracts, accounts, specifications)
            decoration()

        def cardmaker(suppliers_, contracts_, accounts_, specifications_):
            nonlocal suppliers_list
            suppliers_list.clear()
            contracts_list = []
            for supplier in suppliers_:
                suppliers_list.append( Supplier(supplier))
            for contract in contracts_:
                contract_ = Contract(contract)
                for x in suppliers_list:
                    if x.supplier_id == contract['supplier_id']:
                        x.add_contract(contract_)
                        break
                contracts_list.append(contract_)
            for account in accounts_:
                if account['contract_id']:
                    for x in contracts_list:
                        if x.contract_id == account['contract_id']:
                            x.add_account(Account(account))
                            break
                if account['supplier_id']:
                    for x in suppliers_list:
                        if x.supplier_id == account['supplier_id']:
                            x.add_account(Account(account))
                            break
            for specification in specifications_:
                for x in contracts_list:
                    if specification['contract_id'] == x.contract_id:
                        x.add_specification(Specification(specification))

        def decoration():

            panel.controls.clear()
            for sup in suppliers_list:
                sup_card=create_supplier_panel(sup)
                for contract in sup.contracts:
                    contract_card = create_contract_panel(contract)
                    for account in contract.accounts:
                        account_card = create_account_block(account)
                        contract_card.controls.append(account_card)
                    for specification in contract.specifications:
                        specification_card = create_specification_block(specification)
                        contract_card.controls.append(specification_card)
                    sup_card.controls.append(contract_card)
                    if len(contract_card.controls) > 0:
                        contract_card.initially_expanded= True
                for account in sup.accounts:
                    account_card = create_account_block(account)
                    sup_card.controls.append(account_card)
                if len(sup_card.controls) > 0:
                    panel.controls.append(sup_card)


        def read_supplier(_id : int):
            page.client_storage.set('open_element_id', _id)
            page.go("/supplier")
        def read_contract(_id : int):
            page.client_storage.set('open_element_id', _id)
            page.go("/contract")
        def read_account(_id : int):
            page.client_storage.set('open_element_id', _id)
            page.go("/account")
        def read_specification(_id : int):
            page.client_storage.set('open_element_id', _id)
            page.go("/account")

        def apply_filters_callback(credentials):
            token = page.client_storage.get('token')
            suppliers_f, contracts_f, accounts_f, specifications_f = filter_main_page(credentials, token)
            contracts_ = contracts_f
            accounts_ = accounts_f
            specifications_ = specifications_f
            cardmaker(suppliers_f, contracts_, accounts_, specifications_)
            decoration()
            panel.update()

        def search (pattern):
            print('start search')

        def create_supplier_panel(supplier):
            return ft.ExpansionTile(
                title= ft.Row([ft.Text(f'{supplier.name}', **SupplierCardHeaderStyle,
                                       overflow=ft.TextOverflow.ELLIPSIS,
                                       expand=True, 
                                       text_align=ft.TextAlign.LEFT
                                       ),
                               ft.IconButton(icon=ft.Icons.REMOVE_RED_EYE,
                                             on_click=lambda e: read_supplier(supplier.supplier_id)
                                        )]),
                bgcolor= '#805a3b',
                icon_color='#ffffff',
                text_color=ft.Colors.WHITE,
                initially_expanded=True,
                controls_padding = ft.padding.only(left=10),
                tile_padding = ft.padding.only(left=10),
                shape=ft.RoundedRectangleBorder(radius=5)
            )

        def create_contract_panel(contract):
            return ft.ExpansionTile(
                bgcolor='#fd974f',
                icon_color='#ffffff',
                collapsed_bgcolor=ft.Colors.WHITE,
                text_color=ft.Colors.WHITE,
                title=ft.Row([ft.Text(
                    f'Договор: {contract.contract}',
                    **ContractCardHeaderStyle,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True,
                    text_align=ft.TextAlign.LEFT
                ),
                    ft.IconButton(
                        icon=ft.Icons.REMOVE_RED_EYE,
                        on_click=lambda e: read_contract(contract.contract_id)
                        )
                ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                subtitle=ft.Text(contract.lifetime if contract.lifetime else contract.contract_type),
                controls_padding=ft.padding.only(left=20),
                shape=ft.RoundedRectangleBorder(radius=5),
            )

        def create_account_block(account):
            account_ = ft.Text(account.account, **AccountCardHeaderStyle)
            status_ = ft.Text(account.open_status, **AccountCardHeaderStyle)
            status_date_ = ft.Text(account.status_date, **AccountCardHeaderStyle)
            employee_ = ft.Text(account.employee_name, **AccountCardHeaderStyle)
            description_ = ft.Text(account.description, **AccountCardHeaderStyle)
            return ft.Container(
                content= ft.ResponsiveRow(
                    controls=[
                        ft.Column(col=2, controls=[ft.Text('Счёт', **AccountCardHeaderStyle)]),
                        ft.Column(col=2, controls=[account_]),
                        ft.Column(col=2, controls=[status_]),
                        ft.Column(col=2, controls=[status_date_]),
                        ft.Column(col=1, controls=[employee_]),
                        ft.Column(col=3, controls=[description_])
                    ],
                    expand=True,
                ),
                bgcolor=ft.Colors.WHITE,
                on_click=lambda e: read_account(account.account_id),
                expand=True
            )

        def create_specification_block(specification):
            specification_ = ft.Text(specification.specification, **AccountCardHeaderStyle)
            status_ = ft.Text(specification.open_status, **AccountCardHeaderStyle)
            status_date_ = ft.Text(specification.status_date, **AccountCardHeaderStyle)
            employee_ = ft.Text(specification.employee_name, **AccountCardHeaderStyle)
            description_ = ft.Text(specification.description, **AccountCardHeaderStyle)
            return ft.Container(
                content= ft.ResponsiveRow(
                    controls=[
                        ft.Column(col=2, controls=[ft.Text('Спецификация', **AccountCardHeaderStyle)]),
                        ft.Column(col=2, controls=[specification_]),
                        ft.Column(col=2, controls=[status_]),
                        ft.Column(col=2, controls=[status_date_]),
                        ft.Column(col=1, controls=[employee_]),
                        ft.Column(col=3, controls=[description_])
                    ],
                    expand=True,
                ),
                bgcolor=ft.Colors.WHITE,
                on_click=lambda e: read_specification(specification.specification_id),
                expand=True
            )

        def open_close_filters(e):
            filter_column.visible = not filter_column.visible
            page.update()

        #views

        # PAGE

        anchor = ft.SearchBar(
            bar_hint_text="Search",
            view_hint_text="Введите данные",
            on_change=lambda e: search(e.control.value),
            on_submit=lambda e: search(e.control.value),
            autofocus=True
        )

        # PANEL EXAMPLE
        panel = ft.ListView(expand=True,
                            build_controls_on_demand = True,
                            spacing = 10,
                            padding=ft.padding.only(20))

        filter_button = ft.IconButton(width=50,
                                      icon=ft.Icons.FILTER_LIST_ALT,
                                      on_click=lambda e: open_close_filters(e))
        load()
        filter_data = FilterData(
            page=page,
            function_apply=apply_filters_callback,
            close_function=lambda e: open_close_filters(e)
        )
        filter_column = filter_data.create_filters()


        return ft.View('/main',
                       controls=[
                           ft.Stack([
                               ft.Column([
                                   create_nav(page, 0),
                                   filter_button,
                                   anchor,
                                   panel,
                               ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                               filter_column
                           ])
                       ],
                       scroll=ft.ScrollMode.AUTO,
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                       bgcolor=PageBgColor,
                       padding=0
                       )