import  flet as ft
from route import Router
from dotenv import load_dotenv
import logging


load_dotenv()

async def main(page: ft.Page):
    Router(page)

if __name__ == "__main__":
    logging.getLogger("flet_core").setLevel(logging.INFO)
    ft.app(target=main, assets_dir='assets')
