"""Main Module for DatabAIse

Run this to start the Server.
Here is a collection of basic functions, that are used throughout the project.
These are for prompting and for conversion of sql and json formats.
The functions for prompting use strings excessively.
This is because the AI APIs use strings as inputs and return strings.
Probably a conversion is necessary after using them.
"""
import json
import os
import re
import logging

from agents import Agent, Runner, ModelSettings
from openai.types import Reasoning

import Pages
from BaseModels import DatabaseStructure0, DatabaseStructure1, DatabaseStructure3, DatabaseStructure2, Type, _Table3, \
    _Attribute, _DataEntry, CourseTemplate, Course


_course_verify_sample_solutions_to_database_agent = Agent(
    name="sample solution database verifier",
    instructions="""Verify if a list of queries is executable for a specific database.
                 Especially check if the table and attribute names match.
                 Verify if the execution return at least 3 entries for queries that contain ordering and otherwise 
                 at least 1 entry.
                 Replace the queries that do not fulfill the conditions with similar queries that fulfill it.
                 The list of SQL queries contain a 'text' boolean which should also be included unchanged in 
                 your response.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="low"
        )
    ),
    output_type=CourseTemplate
)

_course_verify_sample_solutions_to_course_template_agent = Agent(
    name="sample solution verifier",
    instructions="""Verify if a list of concrete SQL queries match a list of abstract SQL queries.
                 The abstract queries contain instructions inside of square brackets which should be fulfilled
                 in the concrete queries.
                 The concrete queries must not have any additions that are not in the abstracts queries.
                 Alter queries that do not fulfill the condition with similar queries that fulfill it and 
                 return the new concrete queries.
                 The data contain a 'text' boolean which should also be included unchanged in your response.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="low"
        )
    ),
    output_type=CourseTemplate
)

_course_create_sample_solutions_agent = Agent(
    name="sample solution generator",
    instructions="""You are transforming abstract SQL queries to concrete SQL queries for a specific database.
                 The abstract queries contain instructions inside of square brackets.
                 You have to analyze the database and replace the instructions with whatever is asked for.
                 Example-statement: 'SELECT [Spalte1], [Spalte2] FROM [Tabelle1];'
                 Example of your modification: 'SELECT benutzername, level FROM spieler;'
                 You must not add any other additions to the queries.
                 Executing the SQL query must return at least 1 entry.
                 If the query contains ordering it must return at least 3 entries.
                 The input of the abstract SQL queries contain a 'text' boolean
                 which must be kept for the concrete queries.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="low"
        )
    ),
    output_type=CourseTemplate
)

async def course_create_sample_solutions(database: DatabaseStructure3, course_template: CourseTemplate) -> CourseTemplate:
    """Generates SQL statements with a given database and course template.

    :param database: Database with data.
    :param course_template:
        Abstract course template. See :doc:`templates/course_templates` for
        more information.
    :return: Sample solutions for the course.
    """

    result = await Runner.run(_course_create_sample_solutions_agent,
                              f"Generate sample solutions for database: {database.model_dump_json()} with the "
                              f"abstract SQL queries: {course_template.model_dump_json()}.")
    result = await Runner.run(_course_verify_sample_solutions_to_course_template_agent,
                              f"abstract SQL queries: {course_template.model_dump_json()}, "
                              f"concrete SQL queries: {result.final_output.model_dump_json}")
    result = await Runner.run(_course_verify_sample_solutions_to_database_agent,
                              f"SQL queries: {result.final_output.model_dump_json}, "
                              f"database: {database.model_dump_json()}")
    return result.final_output


_course_create_exercise_agent = Agent(
    name="exercise generator",
    instructions="""You are creating exercises for students learning SQL.
                 You get a list of SQL queries which are the solutions for the exercises you have to generate.
                 For SQL queries where the 'text' variable is false the exercise should simply ask for a query by
                 describing the desired result with the tables and attributes.
                 For SQL queries where the 'text' variable is true the exercise should not use explicitly the names of 
                 tables and attributes but give a description a non-technical person would give and a fictive reason for
                 why the SQL query is to be done.
                 The exercises must be in german language.
                 All names of tables or columns should be in single quotation marks.
                 You create also a motivating underlying story line which is explaining the structure of the database.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="low"
        )
    ),
    output_type=Course
)
"""Agent to generate exercises based on SQL queries."""

_course_verify_exercise_agent = Agent(
    name="exercise verifier",
    instructions="""Verify if a list of exercises match the corresponding sample solutions.
                 If it does not match, alter the exercise.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="low"
        )
    ),
    output_type=Course
)
"""Agent to verify that exercises and sample solutions fit."""

async def course_create_exercise(sample_solutions: CourseTemplate) -> Course:
    """Generates underlying story and exercises with sample solutions.

    :param sample_solutions: Concrete sample solutions for the course.
    :return: Course with underlying story and exercises.
    """

    result = await Runner.run(_course_create_exercise_agent,sample_solutions.model_dump_json())
    result = await Runner.run(_course_verify_exercise_agent,
                              f"""Sample solutions: {sample_solutions.model_dump_json()}
                              f"Exercises: {result.final_output.model_dump_json}""")
    return result.final_output


# TODO: Check if conditions are fulfilled.
_db_create_tables_agent = Agent(
    name="table generator",
    instructions="""Generate table names for a database to a given topic.
                 It must be reasonable to have at least two 1-to-many relations, one
                 many-to-many relation and one recursive relation between the tables.
                 The generated tables must not be relational tables.
                 All data must be german or be loanwords for german language.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="low"
        )
    ),
    output_type=DatabaseStructure0
)
"""Agent for generating table names.

The agent is instructed to take into account that the database should have
two 1-to-many relations, one many-to-many-relation and one recursive relation.
"""

async def db_create_tables(topic: str, amount_tables: int = 4) -> DatabaseStructure0:
    """Generates tables to a given topic.

    :param topic: Topic for the database.
    :param amount_tables: Amount of tables to be generated.
    :return: Generated Tables
    """

    result = await Runner.run(_db_create_tables_agent,
                              f"Generate {amount_tables} tables for a database with the topic '{topic}'.")
    return result.final_output



# TODO: Check if conditions are fulfilled.
# TODO: Compare conditions with exercises and add missing conditions.
_db_create_attributes_agent = Agent(
    name="attribute generator",
    instructions="""Generate attribute names for the tables of a database.
                 Primary keys will be incremental integer which must not be any of your suggestions.
                 The suggested attributes must not be secondary keys neither.
                 There has to be at least one table with two attributes with type Integer,
                 one table with two attributes with type Varchar and
                 one table with one attribute with type Integer and one attribute with type Varchar.
                 The output should only include the name of the attribute and not the type.
                 All data must be german or be loanwords for german language.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="none"
        )
    ),
    output_type=DatabaseStructure1
)
"""Agent for generating attributes, used in :func:'db_create_attributes'

The agent is instructed to not generate primary or secondary keys and that the
database should have a table with two integers, a table with two varchar and
a table with one integer and one varchar.
"""

async def db_create_attributes(database: DatabaseStructure0, amount_attributes: int = 3) -> DatabaseStructure1:
    """Generates attributes for each of a collection of tables for a given topic.

    :param database: Database including topic and table names.
    :param amount_attributes: Amount of attributes to be generated per table.
    :return: Database with generated attributes.
    """

    input_string = f"Generate {amount_attributes} attributes for: {database.model_dump_json()}"
    result = await Runner.run(_db_create_attributes_agent, input_string)
    return result.final_output


_db_create_attribute_types_agent = Agent(
    name="attribute type generator",
    instructions="""Generate attribute types for an unfinished database.
                 You are only allowed to use following types: VARCHAR, BOOL, INT, DEC, DATE, DATETIME, TIME and YEAR.
                 The x and y values in the attributes are for the parameters of the type.
                 For example an attribute of type DEC(4, 2) has type=DEC, x=4 and y=2.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="none"
        )
    ),
    output_type=DatabaseStructure2
)
"""Agent for generating attribute types, used in :func:`db_finalize_structure`."""

_db_create_primary_keys_agent = Agent(
    name="primary key generator",
    instructions="""Generate primary keys for every table of an unfinished database.
                 The keys should be IDs with sql naming convention.
                 All data must be german or be loanwords for german language.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="none"
        )
    ),
    output_type=DatabaseStructure2
)
"""Agent for generating primary keys, used in :func:`db_finalize_structure`."""

_db_create_relations_agent = Agent(
    name="relation generator",
    instructions="""Generate relations for the tables of an unfinished database.
                 The relations should be reasonable.
                 But More important are the following conditions:
                 There has to be at least one many-to-many relation, two 1-to-many relations and one recursive relation.
                 You are not allowed to add any table to the database.
                 1-to-many relations are implemented with foreign keys.
                 many-to-many relations are implemented with a relation-table.
                 All data must be german or be loanwords for german language.
                 """,
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="none"
        )
    ),
    output_type=DatabaseStructure2
)
"""Agent for generating relations, used in :func:`db_finalize_structure`.

The agent is instructed to generate at leas one many-to-many relation, two
1-to-many relations and one recursive relation.
"""

_db_verify_relations_agent = Agent(
    name="relation verifier",
    instructions="""Verify if a database contains at least one many-to-many relation,
                    two 1-to-many relations and one recursive relation.
                    If something is missing, add that relation type in the most reasonable way possible.
                    1-to-many relations are implemented with foreign keys.
                    many-to-many relations are implemented with a relation-table.
                    All data must be german or be loanwords for german language.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="none"
        )
    ),
    output_type=DatabaseStructure2
)
"""Agent for verifying the generated relations, used in :func:`db_finalize_structure`."""

async def db_finalize_structure(database: DatabaseStructure1) -> DatabaseStructure2:
    """Generates relations and keys for a given database.

    :param database: database with topic and tables including their attributes.
    :return: Database in json format
    """

    result = await Runner.run(_db_create_attribute_types_agent,database.model_dump_json())
    result = await Runner.run(_db_create_primary_keys_agent, result.final_output.model_dump_json())
    result = await Runner.run(_db_create_relations_agent, result.final_output.model_dump_json())
    result = await Runner.run(_db_verify_relations_agent, result.final_output.model_dump_json())
    return result.final_output


_db_fill_agent = Agent(
    name="database filler",
    instructions="""Fill an empty database with fictive data.
                 The database should have 100 entries total.
                 All data must be german or be loanwords for german language.""",
    model="gpt-5.6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="none"
        )
    ),
    output_type=DatabaseStructure3
)
"""Agent for filling a database with data, used in :func:`db_fill`"""

async def db_fill(db_structure: DatabaseStructure2) -> DatabaseStructure3:
    """Generates data for a given database.

    :param db_structure:
        Database structure.
    :return:
        Database in json format defined by the :data:`example_json`.
    """

    result = await Runner.run(_db_fill_agent,db_structure.model_dump_json())
    return result.final_output


def db_structure_3_to_sql(database: DatabaseStructure3) -> str:
    """Converts a DatabaseStructure3 object to a sql string.

    :param database: database with data.
    :return: String of sql statements to create database.
    """

    logger.info("Converting DatabaseStructure3 object to string")
    if logger.getEffectiveLevel() == logging.DEBUG:
        db_wo_data = {
            "topic": database.topic,
            "tables": [{
                "name": table.name,
                "attributes": [{
                    "name": attribute.name,
                    "type": attribute.type,
                    "x": attribute.x,
                    "y": attribute.y
                } for attribute in table.attributes]
            } for table in database.tables]
        }
        logger.debug(f"DatabaseStructure3 object:\n{json.dumps(db_wo_data, indent=2)}")

    sql_list = []
    sql_list.append(f"CREATE DATABASE '{database.topic}'")
    sql_list.append(f"USE '{database.topic}'")
    logger.debug("Create database")

    foreign_keys = []
    logger.debug("Iterate tables")
    for table in database.tables:
        logger.debug(f"Table '{table.name}'")
        create_table_string = f"CREATE TABLE '{table.name}' ("
        logger.debug("Iterate attributes")
        for attribute in table.attributes:
            logger.debug(f"Attribute '{attribute.name}'")
            create_table_string += f"'{attribute.name}' {attribute.type}"
            if (attribute.type == Type.VARCHAR or attribute.type == Type.INT) and attribute.x != None:
                create_table_string += f"({attribute.x})"
            elif attribute.type == Type.DEC and attribute.x != None and attribute.y != None:
                create_table_string += f"({attribute.x},{attribute.y})"
            create_table_string += ", "
        create_table_string = create_table_string[:-2]
        create_table_string += ")"
        sql_list.append(create_table_string)

        logger.debug("Iterate data entries")
        for entry in table.data_entries:
            insert_entry_string = f"INSERT INTO '{table.name}' VALUES ("
            for value in entry.data_points:
                insert_entry_string += f"'{value}', "
            insert_entry_string = insert_entry_string[:-2]
            insert_entry_string += ")"
            sql_list.append(insert_entry_string)

    sql_string = ""
    for sql_command in sql_list:
        sql_string += f"{sql_command};\n"
    return sql_string


def sql_to_db_structure_3(sql_string: str, disable_debug: bool = True) -> DatabaseStructure3:
    """Converts a sql string to a DatababaseStructure3 object.

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
    :param disable_debug: Prevent log clustering in debug logging level.
    :return: transformed DatabaseStructure3 object.
    """

    logger_level_changed = False
    logger_level: int
    if disable_debug and logger.getEffectiveLevel() == logging.DEBUG:
        logger_level_changed = True
        logger_level = logger.level
        logger.setLevel(logging.INFO)


    logger.info("Converting sql string to DatabaseStructure3 object.")
    logger.debug(f"SQL string:\n{sql_string}")
    topic = ""
    tables: list[_Table3] = []

    # Start of Loop
    queries = sql_string.splitlines()
    query_pointer = 0
    while query_pointer < len(queries):
        query = queries[query_pointer]
        logger.debug(f"Query: {query}")
        words = query.split()

        # Get topic
        if words[0] == "CREATE" and words[1] == "DATABASE":
            logger.debug("Create database")
            topic = re.sub("'", "", words[2])
            query_pointer = query_pointer + 2

        # Get tables
        elif words[0] == "CREATE" and words[1] == "TABLE":
            logger.debug("Create table")
            table_name = words[2].replace("'", "")
            logger.debug(f"table name: {table_name}")
            attributes: list[_Attribute] = []

            # Get attributes
            logger.debug("Getting attributes")
            word_pointer = 3
            while word_pointer < len(words):
                attribute_name = re.sub("['(]", "", words[word_pointer])
                logger.debug(f"Attribute name: {attribute_name}")
                # attribute_full_type is with paremeters. I.e. VARCHAR(255)
                attribute_full_type = words[word_pointer + 1]
                logger.debug(f"Attribute type: {attribute_full_type}")
                attribute_full_type_split = re.split("[(,]", attribute_full_type)
                attribute_full_type_split = [s for s in attribute_full_type_split if s != ""]
                attribute_type_string = attribute_full_type_split[0]
                attribute_type_string = attribute_type_string[:-1] if attribute_type_string.endswith(";") else attribute_type_string
                attribute_type_string = attribute_type_string[:-1] if attribute_type_string.endswith(")") else attribute_type_string
                attribute_type_string = attribute_type_string[:-1] if attribute_type_string.endswith(",") else attribute_type_string
                attribute_type = Type(attribute_type_string)
                attribute_x = None
                attribute_y = None
                if len(attribute_full_type_split) > 1:
                    attribute_x_string = re.sub("[^0-9]", "", attribute_full_type_split[1])
                    attribute_x = int(attribute_x_string)
                if len(attribute_full_type_split) > 2:
                    attribute_y_string = re.sub("[^0-9]", "", attribute_full_type_split[2])
                    attribute_y = int(attribute_y_string)
                if word_pointer + 2 >= len(words):
                    word_pointer = word_pointer + 2
                elif words[word_pointer + 2] == "PRIMARY":
                    attribute_type = Type.INT_PRIMARY_KEY
                    word_pointer = word_pointer + 4
                else:
                    word_pointer = word_pointer + 2

                # Create attribute
                attribute = _Attribute(name=attribute_name, type=attribute_type, x=attribute_x, y=attribute_y)
                attributes.append(attribute)

            # Get data entries
            logger.debug("Getting data")
            data_entries: list[_DataEntry] = []
            while True:
                query_pointer = query_pointer + 1
                if query_pointer >= len(queries):
                    break
                query = queries[query_pointer]
                logger.debug(f"Query: {query}")
                words = query.split()
                if words[0] != "INSERT":
                    break

                #Get data points
                data_points: list[str] = []
                for word_pointer in range(4, len(attributes) + 4):
                    data_points.append(re.sub("[()',;]", "", words[word_pointer]))

                # Create data entry
                data_entry = _DataEntry(data_points=data_points)
                data_entries.append(data_entry)

            # Create table
            table = _Table3(name=table_name, attributes=attributes, data_entries=data_entries)
            tables.append(table)

    # Create database
    database = DatabaseStructure3(topic=topic, tables=tables)
    logger.info("Finished conversion.")

    if logger_level_changed:
        logger.setLevel(logger_level)

    return database


def _check_databases_exist():
    """Checks if databases.db exists."""

    if not os.path.isfile("databases.db"):
        logger.warning("""'databases.db' does not exist. Run 'CreateDatabase.py' to create file and log all databases
                        created with DatabAIse.""")


LOGGING_LEVEL = logging.DEBUG
def create_logger(name: str) -> logging.Logger:
    logger = logging.getLogger("databaise") if name == "" else logging.getLogger(f"databaise.{name}")
    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter("%(asctime)s - %(name)s.%(funcName)s - %(levelname)s: %(message)s")

    file_handler = logging.FileHandler("last_run.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(LOGGING_LEVEL)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(LOGGING_LEVEL)
    logger.addHandler(console_handler)

    logger.setLevel(LOGGING_LEVEL)
    logger.propagate = False

    return logger
logger = create_logger("")



try:
    course_1_db: DatabaseStructure3 \
        = sql_to_db_structure_3(open("course_db/01Kochbuch.sql").read())
    """Database for control group of study for course 1 (cookbook): 
    :doc:`/templates/course_db_1`
    
    :meta hide-value:"""
    course_2_db: DatabaseStructure3 \
        = sql_to_db_structure_3(open("course_db/02Berufsorientierung.sql").read())
    """Database for control group of study for course 2 (career orientation): 
    :doc:`/templates/course_db_2`
    
    :meta hide-value:"""
    course_3_db: DatabaseStructure3 \
        = sql_to_db_structure_3(open("course_db/03Nachbarschafts-Bibliothek.sql").read())
    """Database for control group of study for course 3 (library): 
    :doc:`/templates/course_db_3`
    
    :meta hide-value:"""
    course_4_db: DatabaseStructure3 \
        = sql_to_db_structure_3(open("course_db/04ÖPNV Frankfurt am Main.sql").read())
    """Database for control group of study for course 4 (public transport in Ffm): 
    :doc:`/templates/course_db_4`
    
    :meta hide-value:"""
    course_5_db: DatabaseStructure3 \
        = sql_to_db_structure_3(open("course_db/05Musikarchiv.sql").read())
    """Database for control group of study for course 5 (music archive): 
    :doc:`/templates/course_db_5`
    
    :meta hide-value:"""
    course_6_db: DatabaseStructure3 \
        = sql_to_db_structure_3(open("course_db/06MeilensteineDerWeltgeschichte.sql").read())
    """Database for control group of study for course 6 (milestones of history): 
    :doc:`/templates/course_db_6`
    
    :meta hide-value:"""
    course_template_1: CourseTemplate \
        = CourseTemplate.model_validate_json(open("course_templates/01Projektion.json").read())
    """Template for projection: :doc:`/templates/course_template_1`
    
    :meta hide-value:"""
    course_template_2: CourseTemplate \
        = CourseTemplate.model_validate_json(open("course_templates/02Selektion.json").read())
    """Template for selection: :doc:`/templates/course_template_2`
    
    :meta hide-value:"""
    course_template_3: CourseTemplate \
        = CourseTemplate.model_validate_json(open("course_templates/03Sortierung.json").read())
    """Template for sorting: :doc:`/templates/course_template_3`
    
    :meta hide-value:"""
    course_template_4: CourseTemplate \
        = CourseTemplate.model_validate_json(open("course_templates/04Aggregatsfunktionen.json").read())
    """Template for aggregate functions: :doc:`/templates/course_template_4`
    
    :meta hide-value:"""
    course_template_5: CourseTemplate \
        = CourseTemplate.model_validate_json(open("course_templates/05Join.json").read())
    """Template for joins: :doc:`/templates/course_template_5`
    
    :meta hide-value:"""
    course_template_6: CourseTemplate \
        = CourseTemplate.model_validate_json(open("course_templates/06Unterabfragen.json").read())
    """Template for sub queries: :doc:`/templates/course_template_6`
    
    :meta hide-value:"""
except FileNotFoundError as e:
    # readthedocs has problems reading the file paths. This is a simple and inelegant solution.
    logger.warning(repr(e))


if __name__ == "__main__":
    log_file = open("last_run.log", "w")
    log_file.truncate()
    log_file.close()
    logging.basicConfig()
    _check_databases_exist()
    Pages.build()
