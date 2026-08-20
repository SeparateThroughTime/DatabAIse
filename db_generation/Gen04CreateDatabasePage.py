"""Module for page where the database is created and can be downloaded."""

import json
from nicegui import ui, app, events
import re
import sqlite3
from typing import Dict
from typing import Any

import CssStyles
import DatabAIse


def get_page() -> None:
    """Function to build the page"""

    topic = app.storage.user["topic"]
    tables = app.storage.user["tables"]
    columns = app.storage.user["columns"]

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

    async def start_prompt() -> None:
        response = await DatabAIse.db_create_relations_keys_agent(topic, tables, columns)
        response = await DatabAIse.db_fill_agent(response)

        json_obj = json.loads(response)
        print(json.dumps(json_obj, indent=4))
        _format_json_strings(json_obj)
        sql_string = DatabAIse.json_to_sql(json_obj)
        app.storage.user["sql_string"] = sql_string
        app.storage.user["db_json"] = DatabAIse.sql_to_json(sql_string)
        print(json.dumps(app.storage.user["db_json"], indent=4))

        download_button.on("click", lambda: ui.download.content(sql_string, topic + ".sql"))
        download_button.text = "Download SQL"
        course_button.on("click", lambda: ui.navigate.to("/a/Kurswahl"))
        course_button.text = "Zur Kurswahl"

        con = sqlite3.connect("databases.db")
        cur = con.cursor()
        cur.execute(f"""INSERT INTO databases (topic, sql_file)
                       VALUES ('{app.storage.user["topic"]}', "{app.storage.user["db_json"]}");""")
        con.commit()
        con.close()
    ui.timer(0.1, start_prompt, once=True)


def _format_json_strings(json_obj: Dict[str, Any]) -> None:
    """Helper function to format all strings and names in the json.

    This is primarily to remove or replace illegal characters so the
    SQL engine won't run into errors.

    :param json_obj: JSON to be formatted.
    """

    # Sometime 'topic' is renamed to 'name' from AI...
    if "topic" in json_obj["database"]:
        topic = json_obj["database"]["topic"]
    elif "name" in json_obj["database"]:
        topic = json_obj["database"]["name"]
    else:
        topic = "unknown"
    json_obj["database"]["topic"] = _namingConventions(_replaceUmlaute(topic))

    for table in json_obj["database"]["tables"]:
        table["name"] = _namingConventions(_replaceUmlaute(table["name"]))
        for column in table["columns"]:
            column["name"] = _namingConventions(_replaceUmlaute(column["name"]))
        for entry in table["data"]:
            for value_key in entry:
                entry[value_key] = _replaceUmlaute(_removeApostrophes(entry[value_key]))


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


def _replaceUmlaute(s: str) -> str:
    """Replaces all german umlauts with transliterations"""

    if type(s) is str:
        return re.sub("[Ä]", "Ae", re.sub("[Ö]", "Oe", re.sub("[Ü]", "Ue", re.sub("[ä]", "ae", re.sub("[ö]", "oe", re.sub("[ü]", "ue", re.sub("[ß]", "ss", s)))))))
    else:
        return s
