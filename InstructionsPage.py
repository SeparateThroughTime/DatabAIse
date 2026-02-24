from nicegui import ui, app

from DatabAIse import test_sql
import CssStyles


def on_create_db(self, msg):
    msg.page.redirect = "/Themenwahl"


def on_upload_db(self, msg):
    msg.page.redirect = "/Upload"


def get_page():
    print("Start!")

    ui.restructured_text("Instuktionen").classes(CssStyles.text)

    ui.button("Erstelle Datenbank", on_click=lambda: ui.navigate.to("/Themenwahl")).classes(CssStyles.button)
    ui.button("Lade Datenbank hoch", on_click=lambda: ui.navigate.to("/Upload")).classes(CssStyles.button)