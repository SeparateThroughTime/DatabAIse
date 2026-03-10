from nicegui import ui, app

import CssStyles


def next_page(err_label):
    if "sql_string" not in app.storage.user:
        err_label.visible = True
        return

    ui.navigate.to("/Kurswahl")


async def on_upload(sql_file):
    app.storage.user["sql_string"] = await sql_file.text()


def get_page():
    with ui.card():
        with ui.column():
            ui.markdown("Datenbank hochladen")
            ui.restructured_text("Hier kannst du deine bereits erstellte Datenbank hochladen. Bitte beachte, dass nur Datenbanken funktionieren, die mit diesem Tool erstellt wurden.")
            upload_input = ui.upload(label="SQL-File", max_file_size=16384, on_upload=lambda e: on_upload(e.file), auto_upload=True).props('accept=".sql"')
            err_label = ui.label("Keine Datei ausgewählt!")
            err_label.visible = False
            ui.button("Zur Kurswahl", on_click=lambda: next_page(err_label))