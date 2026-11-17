"""Module for page where the database is created and can be downloaded."""

import logging
import os.path
from typing import override, Optional

from nicegui import ui, app
import sqlite3

import databaise
import logger_module
from base_models import DatabaseStructure1, DatabaseStructure3
import pages

logger: logging.Logger = logger_module.create_logger(__name__)


class CreateDatabasePage(pages.Page):

    _pre_database_build: DatabaseStructure1
    _post_database_build: Optional[DatabaseStructure3]
    _sql_string: str

    def _nav_list_setter(self, val):
        self._nav_list = pages.generate_dynamic_db_generation_nav_list(pages.Pages.CREATE_DATABASE)


    @override
    def save_progress(self):
        if not self._post_database_build:
            return
        self._sql_string = databaise.db_structure_3_to_sql(self._post_database_build)
        app.storage.user["sql_string"] = self._sql_string
        app.storage.user["database_build"][pages.Pages.CREATE_DATABASE] = self._post_database_build.model_dump()
        app.storage.user["courses"] = {}


    @override
    def get_page(self) -> None:
        """Function to build the page"""

        logger.info("Start page build.")
        self._pre_database_build = DatabaseStructure1.model_validate(
            app.storage.user["database_build"][pages.Pages.CHOOSE_ATTRIBUTES])
        self._sql_string = ""
        self._post_database_build = None
        if pages.Pages.CREATE_DATABASE in app.storage.user["database_build"] and not self.prompt:
            self._post_database_build = DatabaseStructure3.model_validate(
                app.storage.user["database_build"][pages.Pages.CREATE_DATABASE])

        with pages.MainCard():
            with ui.column():
                ui.markdown("Erstellen der Datenbank")
                ui.restructured_text("""Du hast es fast geschafft!
                                        Die KI hat nun alle Informationen zum Erstellen der Datenbank. Es werden jetzt Relationen zwischen den Tabellen erzeugt und Daten in die Datenbank eingepflegt.
                                        Es werden möglicherweise noch weitere Tabellen hinzugefügt, damit die Datenbank für alle Aufgaben geeignet ist.
                                        Dieser Schritt kann unter Umständen 1-2 Minuten brauchen.
                                        Im Anschluss kannst du die Datenbank als .sql-Datei herunterladen und zur Kurswahl weitergehen.""")
                with ui.row():
                    self._download_button()
                    ui.button("Zur Kurswahl", on_click=lambda: self.navigate_to(pages.Pages.CHOOSE_COURSE))
        if self.prompt:
            ui.timer(0.1, lambda: pages.wait_for_ai_response_dialog(self._start_prompt), once=True)
        logger.info("Page built.")

    @ui.refreshable
    def _download_button(self):
        download_button = ui.button("Download SQL")
        if self._post_database_build:
            self.save_progress()
            download_button.on("click",
                               lambda: ui.download.content(self._sql_string, self._post_database_build.topic + ".sql"))


    async def _start_prompt(self) -> None:
        logger.debug("Starting prompt to finalize database.")
        response = await databaise.db_finalize_structure(self._pre_database_build)
        logger.debug("Starting prompt to fill database.")
        self._post_database_build = await databaise.db_fill(response)

        self._format_database()
        self.save_progress()

        await self._download_button.refresh()

        if os.path.isfile("databases.db") and self._post_database_build:
            con = sqlite3.connect("databases.db")
            cur = con.cursor()
            cur.execute(f"""INSERT INTO databases (topic, sql_file)
                           VALUES ('{self._post_database_build.topic}', '{self._post_database_build.model_dump_json()}');""")
            con.commit()
            con.close()
        else:
            logger.info("Tried to safe database in 'database.db' but file does not exist.")


    def _format_database(self) -> None:
        """Helper function to format all strings and names in the database.

        This is primarily to remove or replace illegal characters so the
        SQL engine won't run into errors.
        """

        if not self._post_database_build:
            raise TypeError("post database build is None")

        self._post_database_build.topic = databaise.namingConventions(databaise.replaceUmlauts(self._post_database_build.topic))

        for table in self._post_database_build.tables:
            table.name = databaise.namingConventions(databaise.replaceUmlauts(table.name))
            for attribute in table.attributes:
                attribute.name = databaise.namingConventions(databaise.replaceUmlauts(attribute.name))
            for entry in table.data_entries:
                for i in range(len(entry.data_points)):
                    entry.data_points[i] = databaise.replaceUmlauts(databaise.removeApostrophes(entry.data_points[i]))



