from flet_route import Params, Basket
from utils.style import *
from utils.navigation import create_nav


class Profile:

    def view(self, page: ft.Page, params:Params, basket : Basket):
        page.title = "SupplySystem"
        page.theme_mode = 'light'
        page.fonts = pageFont
        page.window.maximized = True
        page.window.title_bar_hidden = False
        page.window.title_bar_buttons_hidden = False

        def page_close_handler(url):
            pass

        return ft.View('/profile',
                   controls=[
                       ft.Stack([
                           ft.Column([
                               create_nav(page, 4, page_close_handler),
                           ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                       ])
                   ],
                   scroll=ft.ScrollMode.AUTO,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   bgcolor=PageBgColor,
                   padding=0
                   )
