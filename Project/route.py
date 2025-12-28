from flet_route import Routing, path
import flet as ft
from pages.welcome_page import WelcomePage
from pages.main_page import MainPage
from pages.suppliers import SuppliersPage
from pages.accounts import AccountsPage
from pages.account import AccountPage
from pages.profile import Profile
from pages.contract import ContractPage
from pages.contracts import ContractsPage




class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.app_routes = [
            path(url="/", clear=True, view=MainPage().view),
            path(url="/main", clear=True, view=MainPage().view),
            path(url="/contracts", clear=True, view=ContractsPage().view),
            path(url="/suppliers", clear=True, view=SuppliersPage().view),
            path(url="/contracts", clear=True, view=ContractsPage().view),
            path(url="/accounts", clear=True, view=AccountsPage().view),
            path(url="/account", clear=True, view=AccountPage().view),
            path(url="/profile", clear=True, view=Profile().view),
            path(url="/contract", clear=True, view=ContractPage().view),
        ]
        Routing(page=self.page, app_routes=self.app_routes)
        self.page.go(self.page.route)
