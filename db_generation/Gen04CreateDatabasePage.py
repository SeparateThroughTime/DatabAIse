import json
from nicegui import ui, app, events
import re
import sqlite3

import CssStyles
import DatabAIse


def get_page():
    topic = app.storage.user["topic"]
    tables = app.storage.user["tables"]
    columns = app.storage.user["columns"]

    with ui.card().style(CssStyles.maincard_style):
        with ui.column():
            ui.markdown("Erstellen der Datenbank")
            ui.restructured_text("""Du hast es fast geschafft!
                                    Die KI hat nun alle Informationen zum Erstellen der Datenbank. Es werden jetzt Relationen zwischen den Tabellen erzeugt und Daten in die Datenbank eingepflegt.
                                    Es werden möglicherweise noch weitere Tabellen hinzugefügt, damit die Datenbank für alle Aufgaben geeignet ist.
                                    Dieser Schritt kann unter Umständen 1-2 Minuten brauchen.""")
            with ui.row():
                download_button = ui.button("Warte auf KI-Antwort")
                course_button = ui.button("Warte auf KI-Antwort")

    ui.timer(0.1, lambda: start_prompt(topic, tables, columns, download_button, course_button), once=True)


async def start_prompt(topic, tables, columns, download_button, course_button):
    response = await DatabAIse.db_create_relations_keys_agent(topic, tables, columns)
    response = await DatabAIse.db_fill_agent(response)

    json_obj = json.loads(response)
    format_json_strings(json_obj)
    sql_string = DatabAIse.json_to_sql(json_obj)
    app.storage.user["sql_string"] = sql_string
    app.storage.user["db_json"] = DatabAIse.sql_to_json(sql_string)

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


def format_json_strings(json_obj):
    json_obj["database"]["topic"] = namingConventions(replaceUmlaute(json_obj["database"]["topic"]))
    for table in json_obj["database"]["tables"]:
        table["name"] = namingConventions(replaceUmlaute(table["name"]))
        for column in table["columns"]:
            column["name"] = namingConventions(replaceUmlaute(column["name"]))
        for entry in table["data"]:
            for value_key in entry:
                entry[value_key] = replaceUmlaute(removeApostrophes(entry[value_key]))


def replaceUmlaute(s):
    if type(s) is str:
        return re.sub("[Ä]", "Ae", re.sub("[Ö]", "Oe", re.sub("[Ü]", "Ue", re.sub("[ä]", "ae", re.sub("[ö]", "oe", re.sub("[ü]", "ue", re.sub("[ß]", "ss", s)))))))
    else:
        return s


def removeApostrophes(s):
    if type(s) is str:
        return re.sub("[']", "", s)
    else:
        return s


def namingConventions(s):
    if type(s is str):
        s = re.sub("[ ]", "_", s.lower())
        return re.sub("[^0123456789abcdefghijklmnopqrstuvwxyz_]", "", s)
    else:
        return s