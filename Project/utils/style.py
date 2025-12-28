import flet as ft

PageBgColor: str ='#ffffff'
pageFont: dict = {
    'NotoSerif-Bold' : "assets/fonts/NotoSerif-Bold.ttf",
    'NotoSerif-Light' : "assets/fonts/NotoSerif-Light.ttf",
    'NotoSerif-Regular' : "assets/fonts/NotoSerif-Regular.ttf",
    'NotoSerif-Thin' : "assets/fonts/NotoSerif-Thin.ttf"
}
pageStyle: dict = {
    'font-family' : 'Roboto-Regular',
}

TitleStyle: dict = {
    'color': "#000000",
    'font_family': 'Roboto-Regular',
}


ButtonWhiteStyle: dict = {
    'bgcolor': {ft.ControlState.HOVERED: '#ffffff', ft.ControlState.DEFAULT: '#F1A1B20'},
    'color' : {ft.ControlState.HOVERED: '#1F222B', ft.ControlState.DEFAULT: '#ffffff'},
    'side': ft.BorderSide(color='#ffffff', width=2),
    'shape': ft.RoundedRectangleBorder(radius=5)
}

ButtonBlueStyle: dict = {
    'bgcolor': '#4B77B4',
    'color' : '#ffffff',
    'shape': ft.RoundedRectangleBorder(radius=5)
}

InputWebFieldStyle: dict = {
    # 'border_width': '0',
    'filled' : True,
    'fill_color' : '31f22b2',
    'text_size' : '12',
    'text_style' : ft.TextStyle(font_family='Roboto-Regular', color='#000000'),
    'border_radius': ft.border_radius.all(5),
    'width': 360,
}


SupplierCardHeaderStyle: dict = {
    'size' : '24',
    'font_family': 'Roboto-Bold'
}

ContractCardHeaderStyle: dict = {
    'size' : '20',
    'font_family': 'Roboto-Regular'
}

AccountCardHeaderStyle: dict = {
    'size' : '18',
    'font_family': 'Roboto-Regular',
    'overflow' : 'ft.TextOverflow.ELLIPSIS',
    'expand' : 'True',
    'text_align' : 'ft.TextAlign.LEFT'
}

NormalMenuButtonStyle: dict = {
    'color' : ft.Colors.WHITE,
    'bgcolor' : '#805a3b',
    'overlay_color' : ft.Colors.TRANSPARENT,
    'elevation' :0,
    'padding' : ft.padding.symmetric(horizontal=20, vertical=15),
    'shape' : ft.RoundedRectangleBorder(radius=0),
    'animation_duration' : 300,
}
ActiveMenuButtonStyle: dict = {
    'color' : ft.Colors.WHITE,
    'bgcolor' : '#4a3423',
    'overlay_color' : ft.Colors.TRANSPARENT,
    'elevation': 2,
    'padding': ft.padding.symmetric(horizontal=20, vertical=15),
    'shape': ft.RoundedRectangleBorder(radius=0),
    'animation_duration': 300
}

ErrorInputStyle: dict = {
    'error_border_style' : ft.border.all(2, ft.Colors.RED_400),
    'error_text_style' : ft.TextStyle(color=ft.Colors.RED_400, size=12)
}

TableTextHeadersStyle: dict = {
    'size' : 14,
    'font_family' : 'NotoSerif-Bold',
    'color' : '#ffffff'
}
TableRowHeadersStyle: dict = {
    'bgcolor' : '#6e4d2e',
    'border' : ft.border.only(bottom= ft.BorderSide(2,'#4a3423' )),
}
TableMainInformationStyle: dict = {
    'color' : '#6e4d2e',
    'size' : 16,
    'font_family' : 'NotoSerif-Bold'
}
TableTextStyle: dict = {
    'size' : 14,
    'font_family' : 'NotoSerif-Regular'
}
TableRowStyle: dict = {
    'border' : ft.border.only(bottom= ft.BorderSide(2, '#4a3423')),
}


### FILTERS

FilterDataTextStyle: dict = {

}

