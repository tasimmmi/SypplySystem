from flet_route import Params, Basket
from utils.style import *
from functional.get_date import load_suppliers
from utils.navigation import create_nav


class SuppliersPage:

    def view(self, page: ft.Page, params: Params, basket: Basket):
        page.title = "SupplySystem"
        page.theme_mode = 'light'
        page.fonts = pageFont
        page.window.maximized = True
        page.window.title_bar_hidden = False
        page.window.title_bar_buttons_hidden = False

        #
        rows = []

        def load():
            nonlocal rows
            token = page.client_storage.get('access_token')
            rows = load_suppliers(token)
            if rows:
                content.controls.append(create_row())
                for row in rows:
                    content.controls.append(create_row(row))

        def open_supplier(supplier_id_):
            page.client_storage.set('open_supplier_id', supplier_id_)
            page.go('/supplier')

        def create_row(row: dict = None):
            supplier_ = ft.GestureDetector(
                content=ft.Text(row.get('name', None), **TableMainInformationStyle),
                on_tap=lambda e: open_supplier(row.get('supplier_id'))
            ) if row else ft.Text('Контрагент', **TableTextHeadersStyle)
            form_ = ft.Text(row.get('form', None), **TableTextStyle) if row else ft.Text('Форма собственности',
                                                                                                  **TableTextHeadersStyle)
            address_ = ft.Text(row.get('address', None), **TableTextStyle) if row else ft.Text('Адрес',
                                                                                                   **TableTextHeadersStyle)
            return ft.Container(
                ft.ResponsiveRow(
                    controls=[
                        ft.Column(col=3, controls=[supplier_]),
                        ft.Column(col=2, controls=[form_]),
                        ft.Column(col=3, controls=[address_]),
                    ],
                    columns=8

                ),
                on_click=lambda e: open_supplier(row.get('supplier_id')),
                padding=ft.padding.all(10),
                alignment=ft.alignment.center,
                #border=ft.border.all(10),
                **TableRowHeadersStyle if not row else TableRowStyle,
            )

        # functions
        def search(pattern: str):
            search_row = [create_row()]
            for row in rows:
                for value in row.values():
                    if isinstance(value, int) or isinstance(value, bool):
                        continue
                    if pattern in value:
                        search_row.append(create_row(row))
                        break
            content.controls = search_row
            content.update()

        content = ft.ListView(width=page.width * 0.5)

        page_name = ft.Container(ft.Text('Контрагенты', **TitleStyle), alignment=ft.alignment.center, margin=20)
        anchor = ft.SearchBar(

            bar_hint_text="Search",
            view_hint_text="Введите данные",
            on_change=lambda e: search(e.control.value),
            on_submit=lambda e: search(e.control.value),
            autofocus=True
        )

        load()
        return ft.View('/suppliers',
                       controls=[
                           ft.Stack([
                               ft.Column([
                                   create_nav(page, 2),
                                   page_name,
                                   anchor,
                                   content
                               ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                           ])
                       ],
                       scroll=ft.ScrollMode.AUTO,
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                       bgcolor=PageBgColor,
                       padding=0
                       )
