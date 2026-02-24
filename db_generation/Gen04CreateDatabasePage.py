import json
from nicegui import ui, app

import CssStyles
import DatabAIse


def get_page():
    topic = app.storage.user["topic"]
    tables = app.storage.user["tables"]
    columns = app.storage.user["columns"]

    download_button = ui.button("Warte auf KI-Antwort").classes(CssStyles.button)
    course_button = ui.button("Warte auf KI-Antwort").classes(CssStyles.button)

    ui.timer(0.1, lambda: start_prompt(topic, tables, columns, download_button, course_button), once=True)


async def start_prompt(topic, tables, columns, download_button, course_button):
    response = await DatabAIse.db_create_relations_keys_agent(topic, tables, columns)
    print(response)
    response = await DatabAIse.db_fill_agent(response)
    print(response)

    json_file = json.loads(response)
    sql_string = create_sql(json_file)
    app.storage.user["sql_string"] = sql_string

    download_button.on("click", lambda: ui.download.content(sql_string, topic + ".sql")).classes(CssStyles.button)
    download_button.text = "Download SQL"
    course_button.on("click", lambda: ui.navigate.to("/Kurswahl")).classes(CssStyles.button)
    course_button.text = "Zur Kurswahl"


def create_sql(json_obj):
    sql_list = []
    sql_list.append("CREATE DATABASE " + json_obj["database"]["topic"])
    sql_list.append("USE " + json_obj["database"]["topic"])

    foreign_keys = []
    for table in json_obj["database"]["tables"]:
        create_table_string = "CREATE TABLE " + table["name"] + " ("
        for column in table["columns"]:
            create_table_string += column["name"] + " " + column["type"]
            if "primary_key" in column:
                create_table_string += " PRIMARY KEY"
            if "foreign_key" in column:
                foreign_key = column["foreign_key"]
                foreign_keys.append((table["name"], column["name"], foreign_key["table"], foreign_key["column"]))
            create_table_string += ", "
        create_table_string = create_table_string[:-2]
        create_table_string += ")"
        sql_list.append(create_table_string)

        for entry in table["data"]:
            insert_entry_string = "INSERT INTO " + table["name"] + " VALUES ("
            for value_key in entry:
                value = entry[value_key]
                insert_entry_string += "'" + str(value) + "', "
            insert_entry_string = insert_entry_string[:-2]
            insert_entry_string += ")"
            sql_list.append(insert_entry_string)

    for foreign_key in foreign_keys:
        table, column, foreign_table, foreign_column = foreign_key
        add_key_string = "ALTER TABLE " + table + " ADD FOREIGN KEY (" + column + ") REFERENCES " + foreign_table + "(" + foreign_column + ")"
        sql_list.append(add_key_string)

    sql_string = ""
    for sql_command in sql_list:
        sql_string += sql_command + ";\n"
    return sql_string