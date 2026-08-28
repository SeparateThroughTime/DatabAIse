"""Module for page where user can upload a database."""

from nicegui.elements.label import Label
from nicegui import ui, app, events
from nicegui.elements.upload_files import FileUpload

import CssStyles
import DatabAIse
import Pages


def get_page(control_group: bool = False) -> None:
    """Function to build the page"""

    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.markdown("Datenbank hochladen")
            ui.restructured_text("Hier kannst du deine bereits erstellte Datenbank hochladen. Bitte beachte, dass nur Datenbanken funktionieren, die mit diesem Tool erstellt wurden.")
            upload_input = ui.upload(label="SQL-File", max_file_size=16384, on_upload=lambda e: _on_upload(e.file), auto_upload=True).props('accept=".sql"')
            err_label = ui.label("Keine Datei ausgewählt!")
            err_label.visible = False
            ui.button("Zur Kurswahl", on_click=lambda: _next_page(err_label, control_group))

    def handle_key(e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            _next_page(err_label, control_group)
    ui.keyboard(on_key=handle_key)


def _next_page(err_label: Label, control_group: bool) -> None:
    """Redirects to ChooseCoursePage if upload was successful."""

    if "sql_string" not in app.storage.user:
        err_label.visible = True
        return

    ui.navigate.to(Pages.get_page_link("choose_course", control_group))


async def _on_upload(sql_file: FileUpload) -> None:
    """Safes uploaded file in user storage."""

    sql_string = await sql_file.text()
    app.storage.user["sql_string"] = sql_string
    app.storage.user["database_build"] = DatabAIse.sql_to_db_structure_3(
        sql_string, disable_debug=False).model_dump_json()