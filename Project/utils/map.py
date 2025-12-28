from utils.style import *
from typing import List
from geopy.geocoders import Photon
import flet_map as map

def user_map (page : ft.Page, coordinates: List[float]
              ):

    marker_layer_ref = ft.Ref[map.MarkerLayer]()
    markers=[]
    no_markers_cord=[53.914022, 27.568092]

    def init_map(e):
        if coordinates != no_markers_cord:
            markers.append(map.Marker(
                content=ft.Text('M'),
                coordinates=map.MapLatitudeLongitude(coordinates[0],coordinates[1]),
            ))

    maps = map.Map(
        expand=True,
        initial_center=map.MapLatitudeLongitude(coordinates[0],coordinates[1]),
        initial_zoom = 11.2,
        on_init = lambda e: init_map(e),
        layers = [
            map.TileLayer(
                url_template='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                on_image_error = lambda e: print('Что-то пошло не так')
            ),
            map.MarkerLayer(
                ref=marker_layer_ref,
                markers=markers
            )
        ]
    )
    page.add(maps)
    return maps
