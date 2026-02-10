import json
import re
from io import StringIO

import justpy
import starlette

import DatabAIse
import CssStyles
import DatabAIse


def on_download(self, msg):
    msg.page.redirect = "/Download"



def on_continue(self, msg):
    msg.page.redirect = "/Kurswahl"


def get_page(request):
    webpage = justpy.WebPage()

    topic = DatabAIse.session_data[request.session_id]["topic"]
    tables = DatabAIse.session_data[request.session_id]["tables"]
    columns = DatabAIse.session_data[request.session_id]["columns"]


    ai_content = "The database has the topic: '" + topic + "'. The database has the tables: "
    for table_index in range(len(tables)):
        ai_content += tables[table_index] + "("
        for column in columns[table_index]:
            ai_content += column + ","
        ai_content = ai_content[:-1]
        ai_content += "), "
    ai_content = ai_content[:-2]
    ai_content += (". Add primary keys to every table as IDs. "
                   "Create reasonable relations between the tables. "
                   "There as to be at least one many-to-many relation and two 1-to-many relations."
                   "You are not allowed to add any table to the database. "
                   "1-to-many relations are implemented with foreign keys. "
                   "many-to-many relations are implemented with a relation-table. "
                   "The output is the database only without explanations or relations.")

    response = DatabAIse.db_generation_prompt(ai_content)
    print(response)
    ai_content = "Fill the Database with 100 entries total." + response + "Let the output fit this example: " + DatabAIse.example_json
    response = DatabAIse.db_generation_prompt(ai_content, False)
    print(response)

    json_file = json.loads(response)
    sql_string = create_sql(json_file)
    DatabAIse.session_data[request.session_id]["sql_string"] = sql_string

    form = justpy.Form(a=webpage, classes=CssStyles.form)

    submit_button = justpy.Input(value="Download", type="submit", a=form, classes=CssStyles.button)
    form.on("submit", on_download)

    return webpage


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