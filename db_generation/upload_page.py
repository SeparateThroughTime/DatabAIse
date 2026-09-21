"""Module for page where user can upload a database."""
from typing import override

from nicegui.elements.button import Button
from nicegui.elements.label import Label
from nicegui import ui, app, events
from nicegui.elements.upload_files import FileUpload

import databaise
import pages


class UploadPage(pages.Page):

    _err_label: Label
    _course_button: Button

    def __init__(self, control_group: bool):
        super().__init__(control_group)


    @override
    def get_page(self) -> None:
        """Function to build the page"""

        with pages.MainCard():
            with ui.column():
                ui.markdown("Datenbank hochladen")
                ui.restructured_text("Hier kannst du deine bereits erstellte Datenbank hochladen. Bitte beachte, dass nur Datenbanken funktionieren, die mit diesem Tool erstellt wurden.")
                ui.upload(label="SQL-File", max_file_size=512288, on_upload=lambda e: self._on_upload(e.file),
                          auto_upload=True, on_rejected=self._on_rejected).props('accept=".sql"')
                self._err_label = pages.ErrorLabel("Keine Datei ausgewählt!")
                self._err_label.visible = False
                self._course_button = ui.button("Zur Kurswahl", on_click=self._next_page).props("disable")
                ui.keyboard(on_key=self._handle_key)


    def _handle_key(self, e: events.KeyEventArguments) -> None:
        if e.action.keydown and e.key.enter:
            self._next_page()


    def _next_page(self) -> None:
        """Redirects to :class:`courses.choos_course_page` if upload was successful."""

        if "sql_string" not in app.storage.user:
            self._err_label.visible = True
            return

        ui.navigate.to(pages.get_page_link("choose_course", self._control_group))


    async def _on_upload(self, sql_file: FileUpload) -> None:
        """Safes uploaded file in user storage."""

        sql_string = await sql_file.text()
        app.storage.user["sql_string"] = sql_string
        app.storage.user["database_build"] = databaise.sql_to_db_structure_3(
            sql_string, disable_debug=False).model_dump_json()
        app.storage.user["courses"] = {}
        self._course_button.props(remove="disable")
        self._err_label.visible = False


    def _on_rejected(self, e) -> None:
        """Notify user for file rejection"""

        self._err_label.text = f"Fehler beim Upload. Eventuell is die Datei zu groß oder der falsche Dateityp."
        self._err_label.visible = True
