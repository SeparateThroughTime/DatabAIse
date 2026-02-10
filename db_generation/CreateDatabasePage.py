import json
import re

import justpy

import DatabAIse
import CssStyles
import DatabAIse


def on_download(self, msg):
    print(msg.page)
    msg.page.redirect = "/Download"
    #msg.page.target = "_blank"
    DatabAIse.session_data[msg.session_id]["msg_form_date"] = msg.form_data


def on_continue(self, msg):
    msg.page.redirect = "/Kurswahl"


def get_page(request):
    webpage = justpy.WebPage()

    topic = -1
    tables = []
    unstructured_columns = []
    columns = [[]]

    for field in DatabAIse.session_data[request.session_id]:
        if field.name == "topic":
            topic = re.sub("[^a-z0-9_]", "", field.value.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss").replace(" ", "_").replace("-", "_").replace(".", "_"))
        elif "table" in field.name:
            tables.append(field.value)
        elif "column" in field.name:
            unstructured_columns.append(field.value)
    columns_per_table = 0
    if len(unstructured_columns) > 0:
        columns_per_table = len(unstructured_columns) // len(tables)
    columns_total_counter = 0
    tables_counter = 0
    while tables_counter < len(tables):
        columns.append([])
        for columns_counter in range(columns_per_table):
            columns[tables_counter].append(unstructured_columns[columns_total_counter])
            columns_total_counter += 1
        tables_counter += 1

    # At the end of columns is an empty list. Don't know why...
    columns.pop()

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

    if columns_per_table <= 0:
        print("Error?")
        return

    response = DatabAIse.db_generation_prompt(ai_content)
    print(response)
    ai_content = "Fill the Database with 100 entries total." + response + "Let the output fit this example: " + DatabAIse.example_json
    response = DatabAIse.db_generation_prompt(ai_content, False)
    print(response)

    json_file = json.loads(response)
    sql_string = create_sql(json_file)

    form = justpy.Form(a=webpage, classes=CssStyles.form)

    topic_input = justpy.Input(a=form, type="hidden", name="topic", value=topic)
    sql_input = justpy.Input(a=form, type="hidden", name="sql", value=sql_string)
    submit_button = justpy.Input(value="Download", type="submit", a=form, classes=CssStyles.button)
    form.on("submit", on_download)

    return webpage


def test_get_page(request):
    webpage = justpy.WebPage()
    print(webpage)
    sql_string = DatabAIse.test_sql

    form = justpy.Form(a=webpage, classes=CssStyles.form)

    topic_input = justpy.Input(a=form, type="hidden", name="topic", value="Test")
    sql_input = justpy.Input(a=form, type="hidden", name="sql", value=sql_string)
    download_button = justpy.Input(value="Download", type="submit", a=form, classes=CssStyles.button)
    form.on("submit", on_download)
    webpage.add()
    continue_button = justpy.Input(value="Weiter zur Kurswahl", a=webpage, classes=CssStyles.button, click=on_continue)

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