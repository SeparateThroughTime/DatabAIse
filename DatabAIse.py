"""Main Module for DatabAIse

Run this to start the Server.
Here is a collection of basic functions, that are used throughout the project.
These are for prompting and for conversion of sql and json formats.
The functions for prompting use strings excessively.
This is because the AI APIs use strings as inputs and return strings.
Probably a conversion is necessary after using them.
"""

import os
import re
import warnings
from typing import List
from typing import Dict
from typing import Any

from openai import OpenAI, AsyncOpenAI
from google import genai
from google.genai import types

import Pages
from nicegui import ui

course_1_db = open("course_db/01Kochbuch.sql").read()
"""Database for control group of study for course 1 (cookbook): 
:doc:`/templates/course_db_1`

:meta hide-value:"""
course_2_db = open("course_db/02Berufsorientierung.sql").read()
"""Database for control group of study for course 2 (career orientation): 
:doc:`/templates/course_db_2`

:meta hide-value:"""
course_3_db = open("course_db/03Nachbarschafts-Bibliothek.sql").read()
"""Database for control group of study for course 3 (library): 
:doc:`/templates/course_db_3`

:meta hide-value:"""
course_4_db = open("course_db/04ÖPNV Frankfurt am Main.sql").read()
"""Database for control group of study for course 4 (public transport in Ffm): 
:doc:`/templates/course_db_4`

:meta hide-value:"""
course_5_db = open("course_db/05Musikarchiv.sql").read()
"""Database for control group of study for course 5 (music archive): 
:doc:`/templates/course_db_5`

:meta hide-value:"""
course_6_db = open("course_db/06MeilensteineDerWeltgeschichte.sql").read()
"""Database for control group of study for course 6 (milestones of history): 
:doc:`/templates/course_db_6`

:meta hide-value:"""
course_template_1 = open("course_templates/01Projektion.json").read()
"""Template for projection: :doc:`/templates/course_template_1`

:meta hide-value:"""
course_template_2 = open("course_templates/02Selektion.json").read()
"""Template for selection: :doc:`/templates/course_template_2`

:meta hide-value:"""
course_template_3 = open("course_templates/03Sortierung.json").read()
"""Template for sorting: :doc:`/templates/course_template_3`

:meta hide-value:"""
course_template_4 = open("course_templates/04Aggregatsfunktionen.json").read()
"""Template for aggregate functions: :doc:`/templates/course_template_4`

:meta hide-value:"""
course_template_5 = open("course_templates/05Join.json").read()
"""Template for joins: :doc:`/templates/course_template_5`

:meta hide-value:"""
course_template_6 = open("course_templates/06Unterabfragen.json").read()
"""Template for sub queries: :doc:`/templates/course_template_6`

:meta hide-value:"""
example_json = open("db_generation/Example.json").read()
"""This is how a db is formatted as json in this project.

See also :doc:`/templates/example_json`

:meta hide-value:"""


async def course_create_exercise(sql_statements: str) -> str:
    """Generates underlying story and exercises for a list of sql statements.

    .. role:: json(code)
        :language: json

    :param sql_statements:
        Sql statements in json format.
        Can be any type that can be cast to string.
        Should have format of :data:`example_json`
    :return:
        | Story and exercises in json format:
        | :json:`{"0": "underlying_story",`
        | :json:`"1": "task_description_1",`
        | :json:`"2": "task_description_2",`
        | ...
        | :json:`"n": "task_description_n"}`

    """

    system_content = ("You are creating exercises for students learning SQL. "
                      "The prompts have following structure:\n"
                      '{"1": {"statement": statement_1, "text": false}, "2": {"statement": statement_2, "text": false}, ..., "n": {"statement": statement_n, "text": true}}\n'
                      "The SQL-Statements are the solutions of the exercises you have to create. "
                      "For SQL-Statements where the text-entry is false the exercise should simply ask for a statement by descriping the desired result with the tables and columns. "
                      "For SQL-Statements where the text-entry is true the exercise should not use the names of tables and columns "
                      "but a description a non-technical person would give and a fictive reason for why the SQL-Statement is to be done. "
                      "The exercises must be in german. Pay attention to a correct german grammar. "
                      "All names of tables or columns should be in single quotation marks. "
                      "You create a motivating underlying story line which is also explaining the structure of the database. "
                      "Your response is only the resulting exercise as json in following structure:"
                      '{"0": underlying_story, "1": task_description_1, "2": task_description_2, ..., "n": task_description_n}\n')
    result = await _main_prompt(system_content, sql_statements, 4, "json")
    return await _course_verify_exercise(sql_statements, result)


async def course_create_sql_statements(db_json: str, course_template_json: str) -> str:
    """Generates sql statements with a given database and course template.

    .. role:: json(code)
        :language: json

    :param db_json:
        Database in json format. Can be any type that can be cast to string.
        Should have format of :data:`example_json`.
    :param course_template_json:
        Json with course template. Can be any type that can be cast to string.
        See :doc:`/templates/course_templates` for more information.
    :return:
        | Sample solutions for the course with json format:
        | :json:`{"1": {"statement": "statement_1", "text": false},`
        | :json:`"2": {"statement": "statement_2", "text": false},`
        | ...
        | :json:`"n": {"statement": "statement_n", "text": true}}`

    """

    system_content = ("You are filling SQL-statements with informations from a database. "
                      "The prompts have following structure:\n"
                      '{"database": database, '
                      '"sql_statements": '
                      '{"1": {"statement": statement_1, "text": false}, "2": {"statement": statement_2, "text": false}, ..., "n": {"statement": statement_n, "text": true}}\n'
                      "The SQL-statements contain instructions inside of square brackets. "
                      "You have to analyze the sql_file and replace the instructions with whatever is asked for. "
                      "Example-statement: 'SELECT [Spalte1], [Spalte2] FROM [Tabelle1];' "
                      "Your modification: 'SELECT benutzername, level FROM spieler;' "
                      "You must not add any other additions to the statements. "
                      "Executing the SQL statements must return at least 1 entry. "
                      "If it contains ordering it must return at least 3 entries. "
                      "Your response is a json in following structure: "
                      '{"1": {"statement": statement_1, "text": false}, "2": {"statement": statement_2, "text": false}, ..., "n": {"statement": statement_n, "text": true}}')
    user_content = f'{{"sql_file": "{db_json}", "exercise_template": {course_template_json}}}'
    result = await _main_prompt(system_content, user_content, 4, "json")
    #return await _course_verify_sql_statements(db_json, result, course_template_json)
    return result


async def db_create_columns_agent(topic: str, tables: List[str]) -> str:
    """Generates 3 columns to each of a collection of tables for a given topic.

    .. role:: json(code)
        :language: json

    :param topic: Topic for the database
    :param tables:
        Tables for the database. Can be any type that can be cast to str but
        list of strings is advised.
    :return:
        | Database structure in json format:
        | :json:`{"table1": ["column1", "column2", "column3"],`
        | ...
        | :json:`"table4": ["column1", "column2", "column3"]}`
    """

    system_content = ("You get a topic and a list of tables for a database. "
                      "Suggest for every table 3 attributes. "
                      "Primary keys will be incremental integer which must not be any of your suggestions. "
                      "The suggested columns must not be secondary keys neither. "
                      "There has to be at least one table with two columns with type Integer, "
                      "one table with two columns with type Varchar and "
                      "one table with one column with type Integer and one column with type Varchar. "
                      "All data must be german or be loanwords for german language. "
                      "The output is a json with following structure: "
                      '{"table1": ["column1", "column2", "column3"], ..., "table4": ["column1", "column2", "column3"]} ')
    user_content = '{topic: ' + topic + "', tables: '" + str(tables) + "'}"
    return await _main_prompt(system_content, user_content, 3, "json")


async def db_create_relations_keys_agent(topic: str, tables: List[str], columns: List[List[str]]) -> str:
    """Generates relations and keys for a given database.

    :param topic: Topic for the database
    :param tables: Tables for the database. Must be a list of strings!
    :param columns:
        Columns for the database. Must be a 2D list of strings! First
        dimension determines table and second dimension determines column.
    :return: Database in json format
    """

    system_content = ("You get the topic, tables and columns for a database. "
                      "Add primary keys to every table as IDs with sql naming convention. "
                      "Create reasonable relations between the tables. "
                      "There has to be at least one many-to-many relation and two 1-to-many relations."
                      "You are not allowed to add any table to the database. "
                      "1-to-many relations are implemented with foreign keys. "
                      "many-to-many relations are implemented with a relation-table. "
                      "All data must be german or be loanwords for german language. "
                      "The output is the database only as json without explanations or relations.")
    user_content = "{topic: '" + topic + "', tables: {"
    for i in range(len(tables)):
        user_content += tables[i] + ": ["
        for j in range(len(columns[i])):
            user_content += columns[i][j] + ", "
        user_content = user_content[:-2] + "], "
    user_content = user_content[:-2] + "}}"
    result = await _main_prompt(system_content, user_content, 3, "json")
    return await _db_verify_relations_keys_agent(result)


async def db_create_tables_agent(topic: str) -> str:
    """Generates 4 tables to a given topic.

    .. role:: json(code)
        :language: json

    :param topic: Topic for the database.
    :return:
        | Tables in json format:
        | :json:`{"A": "table1", "B": "table2", "C": "table3", "D": "table4"}`

    """

    system_content = ("Suggest 4 table names for a database with a specific topic."
                      " It must be reasonable to have at least two 1-to-many relations, one"
                      " many-to-many relation an on recursive relation between the tables."
                      " The suggested tables must not be relational tables."
                      " All data must be german or be loanwords for german language."
                      " The output is a json containing the table names only as:"
                      ' {"A": "table1", "B": "table2", "C": "table3", "D": "table4"}')
    return await _main_prompt(system_content, topic, 3, "json")


async def db_fill_agent(db_json: str) -> str:
    """Generates data for a given database.

    :param db_json:
        Database in json format. Can be any type that can be cast to string.
    :return:
        Database in json format defined by the :data:`example_json`.
    """

    system_content = "You get an empty database. Fill it with 100 entries total. Let the output fit this json example: " + example_json + " Do not use spaces between parameters of a variable type."
    return await _main_prompt(system_content, db_json, 6, "json")


def json_to_sql(json_obj: Dict[str, Any]) -> str:
    """Converts a json to a sql string.

    :param json_obj: Need to be strictly formatted as :data:`example_json`!
    :return: String of sql statements to create database.
    """

    sql_list = []
    sql_list.append("CREATE DATABASE '" + json_obj["database"]["topic"] + "'")
    sql_list.append("USE '" + json_obj["database"]["topic"] + "'")

    foreign_keys = []
    for table in json_obj["database"]["tables"]:
        create_table_string = "CREATE TABLE '" + table["name"] + "' ("
        for column in table["columns"]:
            create_table_string += "'" + column["name"] + "' " + column["type"]
            if "primary_key" in column:
                create_table_string += " PRIMARY KEY"
            #if "foreign_key" in column:
            #    foreign_key = column["foreign_key"]
            #    foreign_keys.append((table["name"], column["name"], foreign_key["table"], foreign_key["column"]))
            create_table_string += ", "
        create_table_string = create_table_string[:-2]
        create_table_string += ")"
        sql_list.append(create_table_string)

        for entry in table["data"]:
            insert_entry_string = "INSERT INTO '" + table["name"] + "' VALUES ("
            for value_key in entry:
                value = entry[value_key]
                insert_entry_string += "'" + str(value) + "', "
            insert_entry_string = insert_entry_string[:-2]
            insert_entry_string += ")"
            sql_list.append(insert_entry_string)

    # Foreign keys made more trouble than they helped, so they were exluded.
    #for foreign_key in foreign_keys:
    #    table, column, foreign_table, foreign_column = foreign_key
    #    add_key_string = ("ALTER TABLE '" + table + "' ADD FOREIGN KEY ('" + column + "') REFERENCES '"
    #                      + foreign_table + "'('" + foreign_column + "')")
    #    sql_list.append(add_key_string)

    sql_string = ""
    for sql_command in sql_list:
        sql_string += sql_command + ";\n"
    return sql_string


def sql_to_json(sql_string: str) -> Dict[str, Any]:
    """Converts a sql string to a json.

    .. role:: sql(code)
        :language: sql

    :param sql_string:
        | Must have exact format:
        | :sql:`CREATE DATABASE db_name;`
        | :sql:`USE db_name;`
        | :sql:`CREATE TABLE table_1(Attributes);`
        | :sql:`INSERT INTO table_1 VALUES(dataset_1);`
        | ...
        | :sql:`INSERT INTO table_1 VALUES(dataset_n);`
        | ...
        | :sql:`CREATE TABLE table_n(Attributes);`
        | :sql:`INSERT INTO table_n VALUES(dataset_1);`
        | ...
        | :sql:`INSERT INTO table_n VALUES(dataset_n);`
    :return: transformed json object.
    """
    json_obj = {}
    database = {}
    json_obj["database"] = database
    tables = []
    database["topic"] = ""
    database["tables"] = tables

    queries = sql_string.splitlines()
    query_pointer = 0
    while query_pointer < len(queries):
        query = queries[query_pointer]
        words = query.split()

        if words[0] == "CREATE" and words[1] == "DATABASE":
            database["topic"] = re.sub("'", "", words[2])
            query_pointer = query_pointer + 2

        elif words[0] == "CREATE" and words[1] == "TABLE":
            table = {}
            tables.append(table)
            table["name"] = words[2].replace("'", "")
            columns = []
            table["columns"] = columns

            word_pointer = 3
            while word_pointer < len(words):
                column = {}
                columns.append(column)
                column["name"] = re.sub("['(]", "", words[word_pointer])
                column_type = words[word_pointer + 1]
                column_type = column_type[:-1] if column_type.endswith(";") else column_type
                column_type = column_type[:-1] if column_type.endswith(")") else column_type
                column_type = column_type[:-1] if column_type.endswith(",") else column_type
                column["type"] = column_type
                if word_pointer + 2 >= len(words):
                    word_pointer = word_pointer + 2
                elif words[word_pointer + 2] == "PRIMARY":
                    column["primary"] = "true"
                    word_pointer = word_pointer + 4
                else:
                    word_pointer = word_pointer + 2

            data = []
            table["data"] = data
            while True:
                query_pointer = query_pointer + 1
                if query_pointer >= len(queries):
                    break
                query = queries[query_pointer]
                words = query.split()
                if words[0] != "INSERT":
                    break

                entry = {}
                data.append(entry)
                for word_pointer in range(4, len(columns) + 4):
                    column_name = columns[word_pointer - 4]["name"]
                    entry[column_name] = re.sub("[()',;]", "", words[word_pointer])

    return json_obj


async def _course_verify_exercise(sql_statements: str, exercises: str) -> str:
    """Helper function for course_create_exercise.

    Verifies and optimizes the generated exercises.

    :param sql_statements:
        Sql statements in json format.
        Can be any type that can be cast to string.
        Should have format of example_json.
    :param exercises: Exercises generated by course_create_exercise.
    :return: Optimized exercises in JSON format.
    """

    system_content = ("You get a json containing exercises and a json with the sample solutions. "
                      "Verify if the exercise fits the corresponding sample solution. "
                      "If it does not fit, change the exercise to fit the sample solution. "
                      "Your response is only the altered json with the exercises in unchanged structure. ")
    user_content = f'exercises: {exercises}, sample_solutions: {sql_statements}'
    result = await _main_prompt(system_content, user_content, 4, "json")
    return result


async def _course_verify_sql_statements(db_json: str, course_json: str, course_template_json: str) -> str:
    """Helper function for course_create_sql_statements.

    Verifies and optimizes the generated sample solution.

    :param db_json:
        Database in json format. Can be any type that can be cast to string.
        Should have format of example_json.
    :param course_json:
        The sample solutions generated by course_create_sql_statements.
    :param course_template_json:
        Database in json format. Can be any type that can be cast to string.
        Should have format of example_json.
    :return: Optimized sample solutions for the course with json format.
    """

    system_content = ("You get a json with a template for SQL queries and a json with corresponding SQL queries. "
                      "Verify if the SQL queries in the second json fit the template and its instructions. "
                      "The second json must not have any additions to the template. "
                      "Alter queries that do not fulfill the condition with similar queries that fulfill it. "
                      "Your response is the altered json in unchanged structure. ")
    user_content = f'template: "{course_template_json}", query_json: {course_json}'
    result1 = await _main_prompt(system_content, user_content, 4, "json")

    system_content = ("You get a json containing a database and a json with a series of SQL queries. "
                      "Verify if the result for the queries that contain ordering return at least 3 entries "
                      "and the result of the other queries return at least 1 entry with the given database. "
                      "Replace the queries that do not fulfill the condition with similar queries that fulfill it. "
                      "Your response is the altered json in unchanged structure. ")
    user_content = f'sql_file: "{db_json}", query_json: {result1}'
    result2 = await _main_prompt(system_content, user_content, 4, "json")
    return result2


async def _db_verify_relations_keys_agent(db_json: str) -> str:
    """Helper function for db_create_relations_keys_agent.

    Verifies and optimizes relation and key generation.

    :param db_json: Database in json format. Can be any type that can be cast to string.
    :return: Optimized database in json format.
    """

    system_content = ("You get the topic, tables and columns for a database. "
                      "Verify if the database contains at least one many-to-many relation "
                      "and two 1-to-many relations. "
                      "If something is missing, add that relation type in the most reasonable way possible. "
                      "1-to-many relations are implemented with foreign keys. "
                      "many-to-many relations are implemented with a relation-table. "
                      "All data must be german or be loanwords for german language. "
                      "The output is the database only as json without explanations or relations.")
    return await _main_prompt(system_content, db_json, 3, "json")


async def _main_prompt(system_content: str, user_content: str, reasoner: int, response_format: str) -> str:
    """This is the function for prompting that should be used by all agents.

    To have multiple options if an AI call throws an exception,
    this method tries different models in a specific order before
    raising an exception if all attempts fail.

    :param system_content: System Content for prompt
    :param user_content: User Content for prompt
    :param reasoner:
        Integer between 0 and 12 determining the 'intelligence' of AI
    :param response_format: Valid formats are "json" and "text"
    """

    try:
        response = await _prompt_gemini(system_content, user_content, reasoner, response_format)
    except Exception as e:
        warnings.warn(str(e), RuntimeWarning)
        try:
            response = await _prompt_deepseek(system_content, user_content, reasoner, response_format)
        except Exception as e:
            warnings.warn(str(e), RuntimeWarning)
            response = "Kritischer Fehler: Keine Kommunikation mit einer KI möglich!"
            with ui.dialog() as dialog:
                ui.label(response)
                ui.button("Ok :(", on_click=dialog.close)
            dialog.open()
            raise Exception("No AI could be used.")
    return response


async def _prompt_deepseek(system_content: str, user_content: str, reasoner: int, response_format: str) -> str:
    """Deepseek API call.

    :param system_content: System content for API call.
    :param user_content: User content for API call.
    :param reasoner:
        Values <= 5 use deepseek-chat. Values > 5 use deepseek-reasoner.
    :param response_format: Can be "json" or "text"
    :return: Only the content of response.
    """

    model = "deepseek-reasoner" if reasoner > 5 else "deepseek-chat"
    response_format = "json_object" if response_format == "json" else "text"
    ai_client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")
    response = ai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": system_content},
            {"role": "user",
             "content": user_content},
        ],
        response_format={'type': response_format},
        stream=False
    )
    return response.choices[0].message.content


async def _prompt_gemini(system_content: str, user_content: str, reasoner: int, response_format: str) -> str:
    """Gemini API call.

    :param system_content: System content for API call
    :param user_content: User content for API call
    :param reasoner:
        0 -> gemini-2.5-flash-lite with 0 thinking budget
        1 -> gemini-2.5-flash-lite with 4096 thinking budget
        2 -> gemini-2.5-flash-lite with 24576 thinking budget
        3 -> gemini-2.5-flash with 0 thinking budget
        4 -> gemini-2.5-flash with 4096 thinking budget
        5 -> gemini-2.5-flash with 24576 thinking budget
        6 -> gemini-3-flash-preview with minimal thinking level
        7 -> gemini-3-flash-preview with low thinking level
        8 -> gemini-3-flash-preview with medium thinking level
        9 -> gemini-3-flash-preview with high thinking level
        10 -> gemini-3.1-pro-preview with low thinking level
        11 -> gemini-3.1-pro-preview with medium thinking level
        12 -> gemini-3.1-pro-preview with high thinking level
    :param response_format:
    :return: Only the content of response.
    """

    match reasoner:
        case 0:
            thinking_config = types.ThinkingConfig(thinking_budget=0)
            model = "gemini-2.5-flash-lite"
        case 1:
            thinking_config = types.ThinkingConfig(thinking_budget=4096)
            model = "gemini-2.5-flash-lite"
        case 2:
            thinking_config = types.ThinkingConfig(thinking_budget=24576)
            model = "gemini-2.5-flash-lite"
        case 3:
            thinking_config = types.ThinkingConfig(thinking_budget=0)
            model = "gemini-2.5-flash"
        case 4:
            thinking_config = types.ThinkingConfig(thinking_budget=4096)
            model = "gemini-2.5-flash"
        case 5:
            thinking_config = types.ThinkingConfig(thinking_budget=24576)
            model = "gemini-2.5-flash"
        case 6:
            thinking_config = types.ThinkingConfig(thinking_level="minimal")
            model = "gemini-3-flash-preview"
        case 7:
            thinking_config = types.ThinkingConfig(thinking_level="low")
            model = "gemini-3-flash-preview"
        case 8:
            thinking_config = types.ThinkingConfig(thinking_level="medium")
            model = "gemini-3-flash-preview"
        case 9:
            thinking_config = types.ThinkingConfig(thinking_level="high")
            model = "gemini-3-flash-preview"
        case 10:
            thinking_config = types.ThinkingConfig(thinking_level="low")
            model = "gemini-3.1-pro-preview"
        case 11:
            thinking_config = types.ThinkingConfig(thinking_level="medium")
            model = "gemini-3.1-pro-preview"
        case 12:
            thinking_config = types.ThinkingConfig(thinking_level="high")
            model = "gemini-3.1-pro-preview"
        case _:
            raise Exception("Unexpected value '" + str(reasoner) + "' for thinking config!")
    match response_format:
        case "json":
            response_format = "application/json"
        case "text":
            response_format = "text/plain"
        case _:
            raise Exception("Unexpected value '" + str(response_format) + "' for response format!")

    ai_client = genai.Client()
    response = await ai_client.aio.models.generate_content(
        model=model,
        contents=user_content,
        config=types.GenerateContentConfig(
            thinking_config=thinking_config,
            system_instruction=system_content,
            responseMimeType=response_format,
            safety_settings=[
                {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_LOW_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_LOW_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_LOW_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_LOW_AND_ABOVE'}
            ]
        )
    )
    return response.candidates[0].content.parts[0].text


async def _prompt_openai(system_content: str, user_content: str, reasoner: int, response_format: str) -> str:
    """OpenAI API call.

    .. attention::

        Function currently uses always text mode as response format!
        During development there was a change in API usage.
        Due to missing time resources it was changed to only use text mode.
        Nonetheless, it does produce correct jsons most of the time.

    :param system_content: System content for API call
    :param user_content: User content for API call
    :param reasoner:
        0-5 -> gpt-5-mini with medium effort
        6,7 -> gpt-5 with low effort
        8 -> gpt-5 with medium effort
        9 -> gpt-5 with high effort
        10 -> gpt-5.4 with medium effort
        11 -> gpt-5.4 with high effort
        12 -> gpt-5.4 with xhigh effort
    :param response_format: Currently not used.
    :return: Only the content of response.
    """

    if reasoner <= 5:
        model = "gpt-5-mini"
        effort = "medium"
    elif reasoner <= 7:
        model = "gpt-5"
        effort = "low"
    elif reasoner <= 8:
        model = "gpt-5"
        effort = "medium"
    elif reasoner <= 9:
        model = "gpt-5"
        effort = "high"
    elif reasoner <= 10:
        model = "gpt-5.4"
        effort = "medium"
    elif reasoner <= 11:
        model = "gpt-5.4"
        effort = "high"
    else:
        model = "gpt-5.4"
        effort = "xhigh"
    ai_client = AsyncOpenAI()
    response = await ai_client.responses.parse(
        model=model,
        reasoning={"effort": effort},
        input=[
            {"role": "system",
             "content": system_content},
            {"role": "user",
             "content": user_content},
        ],
        stream=False
    )
    return response.choices[0].message.content


if __name__ in {"__main__", "__mp_main__"}:
    Pages.build()
