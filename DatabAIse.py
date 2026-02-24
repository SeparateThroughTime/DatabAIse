from openai import OpenAI, AsyncOpenAI
from google import genai
from google.genai import types

import Pages


example_json = open("db_generation/Example.json").read()
test_sql = open("db_generation/Test.sql").read()
course_template_1 = open("course_templates/01Projektion.json").read()
course_template_2 = open("course_templates/02Selektion.json").read()
course_template_3 = open("course_templates/03Sortierung.json").read()
course_template_4 = open("course_templates/04Aggregatsfunktionen.json").read()
course_template_5 = open("course_templates/05Join.json").read()


if __name__ in {"__main__", "__mp_main__"}:
    Pages.build()


async def _current_prompt(system_content, user_content, reasoner, response_format):
    return await _prompt_gemini(system_content, user_content, reasoner, response_format)


async def db_create_tables_agent(topic):
    system_content = ("Suggest 4 table names for a database with a specific topic."
                      " It must be reasonable to have at least two 1-to-many relations and one"
                      " many-to-many relation between the tables."
                      " The suggested tables must not be relational tables."
                      " All data must be german or be loanwords for german language."
                      " The output contains the table names only, as:"
                      ' {"A": "table1", "B": "table2", "C": "table3", "D": "table4"}')
    return await _current_prompt(system_content, topic, 0, "json")


async def db_create_columns_agent(topic, tables):
    system_content = ("You get a topic and a list of tables for a database. "
                      "Suggest for every table 3 attributes. "
                      "Primary keys will be incremental integer which must not be any of your suggestions. "
                      "The suggested columns must not be secondary keys neither. "
                      "There has to be at least one table with two columns with type Integer, "
                      "one table with two columns with type Varchar and "
                      "one table with one column with type Integer and one column with type Varchar. "
                      "All data must be german or be loanwords for german language. "
                      "The output is a json with following structure: "
                      '{"table1": ["column1, column2, column3], ..., "table4": ["column1, column2, column3"]} ')
    user_content = '{topic: ' + topic + "', tables: '" + str(tables) + "'}"
    return await _current_prompt(system_content, user_content, 0, "json")


async def db_create_relations_keys_agent(topic, tables, columns):
    system_content= ("You get the topic, tables and columns for a database. "
                     "Add primary keys to every table as IDs. "
                     "Create reasonable relations between the tables. "
                     "There has to be at least one many-to-many relation and two 1-to-many relations."
                     "You are not allowed to add any table to the database. "
                     "1-to-many relations are implemented with foreign keys. "
                     "many-to-many relations are implemented with a relation-table. "
                     "All data must be german or be loanwords for german language. "
                     "The output is the database only without explanations or relations.")
    user_content = "{topic: '" + topic + "', tables: {"
    for i in range(len(tables)):
        user_content += tables[i] + ": ["
        for j in range(len(columns[i])):
            user_content += columns[i][j] + ", "
        user_content = user_content[:-2] + "], "
    user_content = user_content[:-2] + "}}"
    return await _current_prompt(system_content, user_content, 0, "json")


async def db_fill_agent(database):
    system_content = "You get an empty database. Fill it with 100 entries total. Let the output fit this example: " + example_json
    return await _current_prompt(system_content, database, 0, "json")


async def db_generation_agent(user_content, reasoner=False):
    system_content = ("You are helping to create a database. All data must be in german."
                      "The output is a json file. "
                      "You are not allowed to use sql-keywords for the table names. "
                      "Replace german special characters with characters available in ASCII. "
                      "Use the naming conventions for sql.")
    return await _current_prompt(system_content, user_content, reasoner, "json")


async def course_create_sql_statements(sql_string, course_template_string):
    system_content = ("You are filling SQL-statements with informations from a database. "
                      "The prompts have following structure:\n"
                      '{"sql_file": sql_file, '
                      '"sql_statements": '
                      '{"1": {"statement": statement_1, "text": false}, "2": {"statement": statement_2, "text": false}, ..., "n": {"statement": statement_n, "text": true}}}\n'
                      "The SQL-statements contain instructions inside of square brackets. "
                      "You have to analyze the sql_file and replace the instructions with whatever is asked for. "
                      "Example-statement: 'SELECT [Spalte1], [Spalte2] FROM [Tabelle1];' "
                      "Your modification: 'SELECT benutzername, level FROM spieler;' "
                      "You must not add any other additions to the statements. "
                      "Executing the SQL-statements must return at least one value. "
                      "If it contains ordering it must return at least 4 values."
                      "Your response is a json in following structure:"
                      '{"1": {"statement": statement_1, "text": false}, "2": {"statement": statement_2, "text": false}, ..., "n": {"statement": statement_n, "text": true}}}')
    user_content = f'{{"sql_file": "{sql_string}", "exercise_template": {course_template_string}}}'
    return await _current_prompt(system_content, user_content, 0, "json")


async def course_create_exercise(sql_statements):
    system_content = ("You are creating exercises for students learning SQL. "
                      "The prompts have following structure:\n"
                      '{"1": {"statement": statement_1, "text": false}, "2": {"statement": statement_2, "text": false}, ..., "n": {"statement": statement_n, "text": true}}\n'
                      "The SQL-Statements are the solutions of the exercises you have to create. "
                      "For SQL-Statements where the text-entry is false the exercise should simply ask for a statement by descriping the desired result with the tables and columns. "
                      "For SQL-Statements where the text-entry is true the exercise should not use the names of tables and columns "
                      "but a description a non-technical person would give and a fictive reason for why the SQL-Statement is to be done. "
                      "The exercises must be in german. Pay attention to a correct german grammar. "
                      "All names of tables or columns should be in single quotation marks. "
                      "You create an interesting, catchy and motivating underlying story line. "
                      "Your response is only the resulting exercise as json in following structue:"
                      '{"0": underlying_story, "1": task_1, "2": task_2, ..., "n": task_n}\n')
    return await _current_prompt(system_content, sql_statements, 0, "json")


async def _prompt_deepseek(system_content, user_content, reasoner, response_format):
    model = "deepseek-reasoner" if reasoner else "deepseek-chat"
    ai_client = OpenAI(api_key="sk-d24693c00eac446db4ee589be6eb496e", base_url="https://api.deepseek.com")
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


async def _prompt_openai(system_content, user_content, reasoner, response_format):
    model = "gpt-5-mini-2025-08-07"
    ai_client = AsyncOpenAI(api_key="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")
    response = await ai_client.chat.completions.create(
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


async def _prompt_gemini(system_content, user_content, reasoner, response_format):
    thinking_config = None
    model = None
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
            model = "gemini-3-flash"
        case 7:
            thinking_config = types.ThinkingConfig(thinking_level="low")
            model = "gemini-3-flash"
        case 8:
            thinking_config = types.ThinkingConfig(thinking_level="medium")
            model = "gemini-3-flash"
        case 9:
            thinking_config = types.ThinkingConfig(thinking_level="high")
            model = "gemini-3-flash"
        case 10:
            thinking_config = types.ThinkingConfig(thinking_level="low")
            model = "gemini-3.1-pro"
        case 11:
            thinking_config = types.ThinkingConfig(thinking_level="medium")
            model = "gemini-3.1-pro"
        case 12:
            thinking_config = types.ThinkingConfig(thinking_level="high")
            model = "gemini-3.1-pro"
        case _:
            raise Exception("Unexpected value '" + str(reasoner) + "' for thinking config!")
    match response_format:
        case "json":
            response_format = "application/json"
        case "text":
            response_format = "text/plain"
        case _:
            raise Exception("Unexpected value '" + str(response_format) + "' for response format!")

    ai_client = genai.Client(api_key="AIzaSyD6u0WvtR3YtElrfS0k96gDbl3YWT6S70A")
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