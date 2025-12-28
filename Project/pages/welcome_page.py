import os, requests
import hashlib
import base64
from utils.buttons_and_inputs import button_state
from flet_route import Params, Basket
from utils.style import *

class WelcomePage:

    def view(self, page: ft.Page, params:Params, basket : Basket):
        page.title = "Добро пожаловать!"
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.padding = 20
        page.theme_mode = ft.ThemeMode.DARK
        page.window.width=600
        page.window.height=400
        page.resizable = False

        db_url = os.getenv("URL")

        # Контейнер с изображением
        def image_hover(e):
            e.control.scale = ft.Scale(1.02 if e.data == "true" else 1.0)
            e.control.update()

        def login_link():
            if all([login.value, password.value]):
                credentials = {
                    'login' : login.value,
                }
                response = requests.get(f'{db_url}/api_user/authentication', json=credentials)
                if response.status_code == 200:
                    password_salt = response.json()['salt'][0]
                    password_salt=base64.b64decode(password_salt)
                    print(password_salt)
                    password_hash = hashlib.sha256(password_salt + password.value.encode('utf-8')).hexdigest()
                    credentials['password'] = password_hash
                    response = requests.get(f'{db_url}/api_user/login', json=credentials)
                    if response.status_code == 200:
                        token = response.json().get('access_token')
                        user_id = response.json().get('user_id')
                        page.client_storage.set('access_token', token)
                        page.client_storage.set('user_id', user_id)
                        page.go('/main')
                        return
                    message = f'Неверный пароль'
                message = f'Пользователь не найден' if 'message'  not in locals() else message
                error_api = response.json().get('detail', 'Unknown error')
                print(f'Ошибка входа: {error_api}')
            message = f'Не все данные заполнены' if 'message'  not in locals() else message
            page.open(ft.SnackBar(ft.Text(message)))






        image = ft.Image(
            src="assets/image/human.png",
            height=250,
            #fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(10)
        )
        image.on_hover=image_hover

        login = ft.TextField(width=200, label = 'Login')
        password = ft.TextField(width=200, label = 'Password', password=True)
        button = button_state('Log in',
                                    ButtonBlueStyle,
                                    200, 50,
                                    login_link)

        # Создаем адаптивную структуру
        content = ft.ResponsiveRow(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            columns=12,
            spacing=10,
            #run_spacing=20,
            controls=[
                ft.Column(
                    col={"xs": 5},
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[image],
                    height=280
                ),
                ft.Column(
                    col={"xs": 7},
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        login,
                        password,
                        button
                    ]
                )
            ]
        )

        # Главный контейнер
        container = ft.Container(
            content=content,
            padding=ft.padding.all(30),
            border_radius=ft.border_radius.all(20),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLUE_50,
                offset=ft.Offset(0, 5)
            ),
            alignment=ft.alignment.center
        )

        return ft.View('/',
                       controls= [
                           ft.Column(
                               controls= [container],
                               horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                               scroll=ft.ScrollMode.AUTO
                           )
                       ]
                       )


