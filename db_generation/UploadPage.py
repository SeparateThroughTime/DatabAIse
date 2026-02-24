from nicegui import ui, app

import CssStyles


def next_page():
    if "sql_string" not in app.storage.user:
        ui.label("Keine Datei ausgewählt!").classes(CssStyles.err_msg)
        return

    ui.navigate.to("/Kurswahl")


def on_upload(sql_string):
    app.storage.user["sql_string"] = sql_string


def get_page():
    upload_input = ui.upload(label="SQL-File", max_file_size=16384, on_click=lambda e: on_upload(e.file.text)).props('accept=".sql"').classes(CssStyles.upload)
    ui.button("Zur Kurswahl", on_click=next_page)