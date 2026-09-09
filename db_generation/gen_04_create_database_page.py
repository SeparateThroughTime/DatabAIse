"""Module for page where the database is created and can be downloaded."""

import logging
import os.path
from typing import override

from nicegui import ui, app
import re
import sqlite3

from nicegui.elements.button import Button

import gui_styles
import databaise
import logger_module
from base_models import DatabaseStructure1, DatabaseStructure3
import pages

logger: logging.Logger = logger_module.create_logger(__name__)


class CreateDatabasePage(pages.Page):

    _database_build: DatabaseStructure1 | DatabaseStructure3
    _download_button: Button

    def __init__(self, control_group: bool):
        super().__init__(control_group)


    @override
    def get_page(self) -> None:
        """Function to build the page"""

        logger.info("Start page build.")
        self._database_build = DatabaseStructure1.model_validate(app.storage.user["database_build"])

        with ui.card().style(gui_styles.maincard_style):
            with ui.column():
                ui.markdown("Erstellen der Datenbank")
                ui.restructured_text("""Du hast es fast geschafft!
                                        Die KI hat nun alle Informationen zum Erstellen der Datenbank. Es werden jetzt Relationen zwischen den Tabellen erzeugt und Daten in die Datenbank eingepflegt.
                                        Es werden möglicherweise noch weitere Tabellen hinzugefügt, damit die Datenbank für alle Aufgaben geeignet ist.
                                        Dieser Schritt kann unter Umständen 1-2 Minuten brauchen.
                                        Im Anschluss kannst du die Datenbank als .sql-Datei herunterladen und zur Kurswahl weitergehen.""")
                with ui.row():
                    self._download_button = ui.button("Download SQL")
                    ui.button("Zur Kurswahl", on_click=lambda: ui.navigate.to(pages.get_page_link(
                        "choose_course", self._control_group)))
        ui.timer(0.1, lambda: pages.wait_for_ai_response_dialog(self._start_prompt), once=True)
        logger.info("Page built.")

    async def _start_prompt(self) -> None:
        logger.debug("Starting prompt to finalize database.")
        if isinstance(self._database_build, DatabaseStructure1):
            response = await databaise.db_finalize_structure(self._database_build)
        else:
            raise TypeError(f"Expected DatabaseStructure1 but got {type(self._database_build)}")
        logger.debug("Starting prompt to fill database.")
        self._database_build = await databaise.db_fill(response)

        self._format_database()
        if isinstance(self._database_build, DatabaseStructure3):
            sql_string = databaise.db_structure_3_to_sql(self._database_build)
        else:
            raise TypeError(f"Expected DatabaseStructure3 but got {type(self._database_build)}")
        app.storage.user["sql_string"] = sql_string
        app.storage.user["database_build"] = self._database_build.model_dump_json()
        app.storage.user["courses"] = {}

        self._download_button.on("click",
                                 lambda: ui.download.content(sql_string, self._database_build.topic + ".sql"))

        if os.path.isfile("databases.db"):
            con = sqlite3.connect("databases.db")
            cur = con.cursor()
            cur.execute(f"""INSERT INTO databases (topic, sql_file)
                           VALUES ('{self._database_build.topic}', '{self._database_build.model_dump_json()}');""")
            con.commit()
            con.close()
        else:
            logger.info("Tried to safe database in 'database.db' but file does not exist.")


    def _format_database(self) -> None:
        """Helper function to format all strings and names in the database.

        This is primarily to remove or replace illegal characters so the
        SQL engine won't run into errors.
        """

        if not isinstance(self._database_build, DatabaseStructure3):
            raise TypeError(f"Expected DatabaseStructure3 but got {type(self._database_build)}")

        self._database_build.topic = self._namingConventions(self._replaceUmlauts(self._database_build.topic))

        for table in self._database_build.tables:
            table.name = self._namingConventions(self._replaceUmlauts(table.name))
            for attribute in table.attributes:
                attribute.name = self._namingConventions(self._replaceUmlauts(attribute.name))
            for entry in table.data_entries:
                for i in range(len(entry.data_points)):
                    entry.data_points[i] = self._replaceUmlauts(self._removeApostrophes(entry.data_points[i]))


    @staticmethod
    def _namingConventions(s: str) -> str:
        """Tries to fit str to SQL naming conventions

        Spaces are replaced with uncerscores, uppercase letters with lowercase
        letters and then everything except numbers, letters and underscores
        removed.
        """
        if type(s is str):
            s = re.sub("[ ]", "_", s.lower())
            return re.sub("[^0123456789abcdefghijklmnopqrstuvwxyz_]", "", s)
        else:
            return s


    @staticmethod
    def _removeApostrophes(s: str) -> str:
        """Removes all apostrophes"""

        if type(s) is str:
            return re.sub("[']", "", s)
        else:
            return s


    @staticmethod
    def _replaceUmlauts(s: str) -> str:
        """Replaces all german umlauts with transliterations"""

        if type(s) is str:
            return re.sub("[Ä]", "Ae", re.sub("[Ö]", "Oe", re.sub("[Ü]", "Ue", re.sub("[ä]", "ae", re.sub("[ö]", "oe", re.sub("[ü]", "ue", re.sub("[ß]", "ss", s)))))))
        else:
            return s
