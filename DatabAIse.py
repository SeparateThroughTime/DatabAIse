from openai import OpenAI
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
session_data = {}


if __name__ == "__main__":
    Pages.build()


def db_generation_prompt(user_content, reasoner=False):
    system_content = ("You are helping to create a database. All data must be in german."
                      "The output is a json file. "
                      "You are not allowed to use sql-keywords for the table names. "
                      "Replace german special characters with characters available in ASCII. "
                      "Use the naming conventions for sql.")
    return _prompt_openai(system_content, user_content, reasoner, "json_object")


def course_generation_prompt(sql_string, course_template_string, reasoner=True):
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
    response = _prompt_openai(system_content, user_content, reasoner, "json_object")
    print(response)

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
    return _prompt_openai(system_content, response, reasoner, "json_object")


def _prompt_deepseek(system_content, user_content, reasoner, response_format):
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


def _prompt_openai(system_content, user_content, reasoner, response_format):
    model = "gpt-5-nano"
    ai_client = OpenAI(api_key="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")
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

def _prompt_gemini(system_content, user_content, reasoner, response_format):
    model = "gemini-3-flash-preview"
    ai_client = genai.Client(api_key="AIzaSyD6u0WvtR3YtElrfS0k96gDbl3YWT6S70A")
    response = ai_client.models.generate_content(
        model=model,
        contents=user_content,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
            system_instruction=system_content,
            responseMimeType="application/json"
        )
    )
    return response.candidates[0].content.parts[0].text


