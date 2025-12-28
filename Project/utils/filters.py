import flet as ft

from functional.get_date import suppliers_name
from utils.buttons_and_inputs import button_state, input_hint, calendar_button
from utils.style import ButtonWhiteStyle, ButtonBlueStyle, FilterDataTextStyle


class FilterData:
    def __init__(self, page,function_apply, close_function):
        self.page = page
        self.suppliers = suppliers_name()
        self.function_apply = function_apply
        self.close_function = close_function

        self._init_elements()

    def _init_elements(self):

        self.supplier_checkboxes = ft.Column(controls=[])
        for supplier in self.suppliers:
            self.supplier_checkboxes.controls.append(
                ft.Checkbox(
                    label=supplier['name'],
                    value=True,
                    key=supplier['supplier_id']
                )
            )

        self.status_filter = ft.Dropdown(
            editable=True,
            label="Активность",
            options=[
                ft.dropdown.Option(text="Открыт"),
                ft.dropdown.Option(text="Закрыт"),
                ft.dropdown.Option(text="Ожидает поставку"),
                ft.dropdown.Option(text="Ожидает оплату")
            ],
            enable_filter=True,
            width=170,
            label_style=ft.TextStyle(size=12),
        )

        self.activity_checkbox = ft.Checkbox(
            label='Действующие',
            tristate=True,
            value=None
        )

        self.employee_checkbox = ft.Checkbox(
            label='Мои договора'
        )

        self.contract_from = ft.Text('----/--/--', **FilterDataTextStyle)
        self.contract_to = ft.Text('----/--/--', **FilterDataTextStyle)
        self.payment_from = ft.Text('----/--/--', **FilterDataTextStyle)
        self.payment_to = ft.Text('----/--/--', **FilterDataTextStyle)
        self.delivery_from = ft.Text('----/--/--', **FilterDataTextStyle)
        self.delivery_to = ft.Text('----/--/--', **FilterDataTextStyle)

        self.select_all_checkbox = ft.Checkbox(
                        label="Выбрать все",
                        value=True,
                        on_change=lambda e: self.activate_all_suppliers()
                    )

        self.clean_button = button_state(
            'Отменить',
            ButtonWhiteStyle,
            100, 50,
            self.clear_filters
        )

        self.apply_button = button_state(
            'Применить',
            ButtonBlueStyle,
            100, 50,
            self.apply_filters
        )

    def create_filters(self):

        checkbox_area = ft.Container(
            ft.Column(
                controls=[
                    ft.Text('Контрагенты'),
                    ft.SearchBar(
                        bar_hint_text="Поиск",
                        view_hint_text="Введите данные",
                        on_change=lambda e: self.search(e.control.value),
                        on_submit=lambda e: self.search(e.control.value),
                        autofocus=True,
                        height=30
                    ),
                    self.select_all_checkbox,
                    self.supplier_checkboxes
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            border_radius=5,
            border=ft.border.all(1, ft.Colors.BLACK),
            height=200,
            width=250
        )

        contract_area = ft.Column(
            controls=[
                input_hint("По дате заключения"),
                ft.Row(
                    controls=[
                        self.contract_from,
                        calendar_button(self.page, 50, self.contract_from),
                        self.contract_to,
                        calendar_button(self.page, 50, self.contract_to)
                    ]
                )
            ]
        )

        payment_area = ft.Column(
            controls=[
                input_hint("По дате оплаты"),
                ft.Row(
                    controls=[
                        self.payment_from,
                        calendar_button(self.page, 50, self.payment_from),
                        self.payment_to,
                        calendar_button(self.page, 50, self.payment_to)
                    ]
                )
            ]
        )

        delivery_area = ft.Column(
            controls=[
                input_hint("По дате поставки"),
                ft.Row(
                    controls=[
                        self.delivery_from,
                        calendar_button(self.page, 50, self.delivery_from),
                        self.delivery_to,
                        calendar_button(self.page, 50, self.delivery_to)
                    ]
                )
            ]
        )

        filter_column = ft.Container(
            ft.Column([
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    on_click=self.close_function,
                ),
                ft.Text('Фильтры', size=20, weight=ft.FontWeight.BOLD),
                checkbox_area,
                self.status_filter,
                self.activity_checkbox,
                self.employee_checkbox,
                contract_area,
                payment_area,
                delivery_area,
                ft.Row([
                    self.clean_button,
                    self.apply_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=15,
            scroll=ft.ScrollMode.AUTO),
            visible=False,
            height=800,
            width=300,
            alignment=ft.alignment.Alignment(-1, 0),
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.center_left,
                end=ft.alignment.center_right,
                colors=[
                    ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                    ft.Colors.with_opacity(0.7, ft.Colors.WHITE),
                    ft.Colors.with_opacity(0.9, '#4a3423'),
                ]
            ),
            border_radius=10,

        )

        return filter_column

    def apply_filters(self):
        credentials = {}

        # Сбор выбранных поставщиков
        names = []
        for supplier in self.supplier_checkboxes.controls:
            if supplier.value:
                names.append(supplier.key)
        if names:
            credentials['supplier_filter'] = names

        # Сбор других фильтров
        if self.status_filter.value:
            credentials['open_status_filter'] = self.status_filter.value

        if self.activity_checkbox.value is not None:
            credentials['activity_filter'] = self.activity_checkbox.value

        if self.employee_checkbox.value:
            credentials['employee_filter'] = self.page.client_storage.get('user_id')

        date_fields = {
            'contract_from': self.contract_from,
            'contract_to': self.contract_to,
            'payment_from': self.payment_from,
            'payment_to': self.payment_to,
            'delivery_from': self.delivery_from,
            'delivery_to': self.delivery_to
        }

        for key, field in date_fields.items():
            if field.value and field.value != '----/--/--':
                credentials[key] = field.value

        self.function_apply(credentials)

    def clear_filters(self):
        for checkbox in self.supplier_checkboxes.controls:
            checkbox.value = True

        self.select_all_checkbox.value = True

        self.status_filter.value = None
        self.activity_checkbox.value = None
        self.employee_checkbox.value = False

        date_fields = [
            self.contract_from, self.contract_to,
            self.payment_from, self.payment_to,
            self.delivery_from, self.delivery_to
        ]

        for field in date_fields:
            field.value = '----/--/--'

        self.supplier_checkboxes.update()
        self.select_all_checkbox.update()
        self.status_filter.update()
        self.activity_checkbox.update()
        self.employee_checkbox.update()

        for field in date_fields:
            field.update()

    def search(self, pattern):
        pattern_sup = []
        for supplier in self.suppliers:
            if pattern.lower() in supplier['name'].lower():
                pattern_sup.append(
                    ft.Checkbox(
                        label=supplier['name'],
                        value=True,
                        key=supplier['supplier_id']
                    )
                )
        self.supplier_checkboxes.controls = pattern_sup
        self.supplier_checkboxes.update()

    def activate_all_suppliers(self):

        for checkbox in self.supplier_checkboxes.controls:
            checkbox.value = self.select_all_checkbox.value

        self.supplier_checkboxes.update()


class AccountSpecifFilter(FilterData):
    def __init__(self, page, function_apply, close_function):
        super().__init__(page, function_apply, close_function)

        # Инициализация дополнительного Dropdown
        self.additional_filter = ft.Dropdown(
            editable=True,
            hint_text="Тип документа",
            options=[
                ft.dropdown.Option(text="Счет"),
                ft.dropdown.Option(text="Спецификация")
            ],
            enable_filter=True,
            width=170,
            label_style=ft.TextStyle(size=12)
        )

    def create_filters(self):
        base_filter = super().create_filters()
        filter_content = base_filter.content

        filter_content.controls.insert(
            filter_content.controls.index(self.employee_checkbox) + 1,
            self.additional_filter
        )

        return base_filter

    def apply_filters(self):
        credentials = {}
        super().apply_filters()

        if self.additional_filter.value:
            credentials['document_type'] = self.additional_filter.value

        self.function_apply(credentials)

    def clear_filters(self):
        super().clear_filters()

        self.additional_filter.value = None
        self.additional_filter.update()
