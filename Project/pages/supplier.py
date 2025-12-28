from flet_route import Params, Basket
from utils.style import *
from utils.navigation import create_nav

class SupplierPage:

    def view(self, page: ft.Page, params:Params, basket : Basket):
        page.title = "SupplySystem"
        page.theme_mode = 'light'
        page.fonts = pageFont
        page.window.maximized = True
        page.window.title_bar_hidden = False
        page.window.title_bar_buttons_hidden = False

        supplier_id = page.client_storage.get('open_element_id')
        contract, documents = {}, []


        def load():
            nonlocal contract , documents
            token = page.client_storage.get('access_token')
            # contract, documents = load_contract(token, contact_id)
            # contract_decoration(contract)
            # table_decoration(documents)

        return ft.View('/contracts',
                       controls=[
                           ft.Stack([
                               ft.Column([
                                   create_nav(page, 1),
                               ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                           ])
                       ],
                       scroll=ft.ScrollMode.AUTO,
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                       bgcolor=PageBgColor,
                       padding=0
                       )
