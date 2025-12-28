import flet as ft
from utils.style import NormalMenuButtonStyle, ActiveMenuButtonStyle

def create_nav(page, index=None, func=None):
    # Цветовая схема
    PRIMARY_COLOR = '#805a3b'
    HOVER_COLOR = '#694a31'
    ACTIVE_COLOR = '#4a3423'
    TEXT_COLOR = ft.Colors.WHITE

    # Создаем кнопки навигации
    nav_buttons = [
        ft.Container(
            ft.ElevatedButton(
                text='Главная',
                on_click=lambda e: func('/main') if func else page.go('/main'),
                style=ft.ButtonStyle(**NormalMenuButtonStyle),
            ),
            height=40,
        ),
        ft.Container(
            ft.ElevatedButton(
                text='Договора',
                on_click=lambda e: func('/contracts') if func else page.go('/contracts'),
                style=ft.ButtonStyle(**NormalMenuButtonStyle),
            ),
            height=40,
        ),
        ft.Container(
            ft.ElevatedButton(
                text='Контрагенты',
                on_click=lambda e: func('/suppliers') if func else page.go('/suppliers'),
                style=ft.ButtonStyle(**NormalMenuButtonStyle),
            ),
            height=40,
        ),
        ft.Container(
            ft.ElevatedButton(
                text='Счета/Спецификации',
                on_click=lambda e: func('/accounts') if func else page.go('/accounts'),
                style=ft.ButtonStyle(**NormalMenuButtonStyle),
            ),
            height=40,
        ),
        ft.Container(
            ft.ElevatedButton(
                text='Профиль',
                on_click=lambda e: func('/profile') if func else page.go('/profile'),
                style=ft.ButtonStyle(**NormalMenuButtonStyle),
            ),
            height=40,
        )
    ]

    nav_buttons[index].content.style = ft.ButtonStyle(**ActiveMenuButtonStyle)
    nav_buttons[index].border= ft.border.only(bottom=ft.border.BorderSide(1, "white"))

    # Добавляем эффекты при наведении
    for i, button in enumerate(nav_buttons):
        if i != index:  # Не применяем к активной кнопке
            button.content.on_hover = lambda e, btn=button.content: hover_effect(e, btn)

    def hover_effect(e, button):
        if e.data == "true":
            button.style.bgcolor = HOVER_COLOR
            button.style.elevation = 1
        else:
            button.style.bgcolor = PRIMARY_COLOR
            button.style.elevation = 0
        button.update()

    # Создаем контейнер с навигацией
    nav = ft.Container(
        content=ft.Row(
            controls=nav_buttons,
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor=PRIMARY_COLOR,
        padding=ft.padding.only(left=20),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            #color=ft.Colors.BLACK.with_opacity(0.2),
            offset=ft.Offset(0, 3)
        )
    )

    return nav

