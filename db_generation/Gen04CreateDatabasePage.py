"""Module for page where the database is created and can be downloaded."""

import logging
import os.path

from nicegui import ui, app, events
import re
import sqlite3

import CssStyles
import DatabAIse
import logger_module
from BaseModels import DatabaseStructure1, DatabaseStructure3
import Pages


logger: logging.Logger = logger_module.create_logger(__name__)


def get_page(control_group: bool = False) -> None:
    """Function to build the page"""

    logger.info("Start page build.")
    database_build : DatabaseStructure1 = DatabaseStructure1.model_validate(app.storage.user["database_build"])
    topic = database_build.topic

    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.markdown("Erstellen der Datenbank")
            ui.restructured_text("""Du hast es fast geschafft!
                                    Die KI hat nun alle Informationen zum Erstellen der Datenbank. Es werden jetzt Relationen zwischen den Tabellen erzeugt und Daten in die Datenbank eingepflegt.
                                    Es werden möglicherweise noch weitere Tabellen hinzugefügt, damit die Datenbank für alle Aufgaben geeignet ist.
                                    Dieser Schritt kann unter Umständen 1-2 Minuten brauchen.
                                    Im Anschluss kannst du die Datenbank als .sql-Datei herunterladen und zur Kurswahl weitergehen.""")
            with ui.row():
                download_button = ui.button("Warte auf KI-Antwort")
                course_button = ui.button("Warte auf KI-Antwort")
    logger.info("Page built.")

    async def start_prompt() -> None:
        logger.debug("Starting prompt to finalize database.")
        response = await DatabAIse.db_finalize_structure(database_build)
        logger.debug("Starting prompt to fill database.")
        database = await DatabAIse.db_fill(response)

        _format_database(database)
        sql_string = DatabAIse.db_structure_3_to_sql(database)
        app.storage.user["sql_string"] = sql_string
        app.storage.user["database_build"] = database.model_dump_json()

        download_button.on("click", lambda: ui.download.content(sql_string, topic + ".sql"))
        download_button.text = "Download SQL"
        course_button.on("click", lambda: ui.navigate.to(Pages.get_page_link("choose_course", control_group)))
        course_button.text = "Zur Kurswahl"

        if os.path.isfile("databases.db"):
            con = sqlite3.connect("databases.db")
            cur = con.cursor()
            cur.execute(f"""INSERT INTO databases (topic, sql_file)
                           VALUES ('{app.storage.user["topic"]}', "{app.storage.user["db_json"]}");""")
            con.commit()
            con.close()
        else:
            logger.info("Tried to safe database in 'database.db' but file does not exist.")
    ui.timer(0.1, start_prompt, once=True)


def _format_database(database: DatabaseStructure3) -> None:
    """Helper function to format all strings and names in the database.

    This is primarily to remove or replace illegal characters so the
    SQL engine won't run into errors.

    :param json_obj: JSON to be formatted.
    """

    database.topic = _namingConventions(_replaceUmlauts(database.topic))

    for table in database.tables:
        table.name = _namingConventions(_replaceUmlauts(table.name))
        for attribute in table.attributes:
            attribute.name = _namingConventions(_replaceUmlauts(attribute.name))
        for entry in table.data_entries:
            for i in range(len(entry.data_points)):
                entry.data_points[i] = _replaceUmlauts(_removeApostrophes(entry.data_points[i]))


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


def _removeApostrophes(s: str) -> str:
    """Removes all apostrophes"""

    if type(s) is str:
        return re.sub("[']", "", s)
    else:
        return s


def _replaceUmlauts(s: str) -> str:
    """Replaces all german umlauts with transliterations"""

    if type(s) is str:
        return re.sub("[Ä]", "Ae", re.sub("[Ö]", "Oe", re.sub("[Ü]", "Ue", re.sub("[ä]", "ae", re.sub("[ö]", "oe", re.sub("[ü]", "ue", re.sub("[ß]", "ss", s)))))))
    else:
        return s
