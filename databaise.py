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

import pages
import logger_module
from base_models import DatabaseStructure0, DatabaseStructure1, DatabaseStructure3, DatabaseStructure2, Type, _Table3, \
    _Attribute, _DataEntry, CourseTemplate, Course, ORPHANED_MIN, ORPHANED_MAX, UNREFERENCED_MIN, UNREFERRED_MAX

MAX_TABLES: int = 100

MAX_ATTRIBUTES: int = 5


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
                 The SQL query must not return the same result as an reduction of it.
                 For this you have to check for example if a query which is filtering orphaned records actually relates
                 to a dataset with existing orphaned records.
                 The input of the abstract SQL queries contain a 'text' boolean
                 which must be kept for the output.""",
    model="gpt-6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="high"
        )
    ),
    output_type=CourseTemplate
)
"""Agent for generating sample solutions."""


async def course_create_sample_solutions(database: DatabaseStructure3, course_template: CourseTemplate) -> CourseTemplate:
    """Generates SQL statements with a given database and course template.

    :param database: Database with data.
    :param course_template:
        Abstract course template. See :doc:`/templates/course_templates` for
        more information.
    :return: Sample solutions for the course.
    """

    result = await Runner.run(_course_create_sample_solutions_agent,
                              f"Generate sample solutions for database: {database.model_dump_json()} with the "
                              f"abstract SQL queries: {course_template.model_dump_json()}.")
    logger.debug(f"_course_create_sample_solutions_agent produced:\n{result.final_output.model_dump_json(indent=2)}")
    return result.final_output


_course_create_story_agent = Agent(
    name="story generator",
    instructions="""You get a database to a specific topic which is used for learning purpose.
                 Your task is to generate a motivating underlying story line for the database.
                 The story must be in german language and should not exceed 100 words.""",
    model="gpt-6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="none"
        )
    ),
    output_type=str
)


_course_create_exercise_agent = Agent(
    name="exercise generator",
    instructions="""You are creating exercises for students learning SQL.
                 You get a background story for the database and 
                 a list of SQL queries which are the solutions for the exercises you have to generate.
                 For SQL queries where the 'text' variable is false the exercise should simply ask for a query by
                 describing the desired result with the tables and attributes.
                 For SQL queries where the 'text' variable is true the exercise should not use explicitly the names of 
                 tables and attributes but give a description a non-technical person would give and a fictive reason for
                 why the SQL query is to be done.
                 The exercises must be in german language.
                 All names of tables or attributes should be in single quotation marks.""",
    model="gpt-6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="high"
        )
    ),
    output_type=Course
)
"""Agent to generate exercises based on SQL queries."""

async def course_create_exercise(sample_solutions: CourseTemplate, database: DatabaseStructure3) -> Course:
    """Generates exercises with sample solutions.

    :param sample_solutions: Concrete sample solutions for the course.
    :param database: Database structure.
    :return: Course with underlying story and exercises.
    """


    story = await Runner.run(_course_create_story_agent, database.model_dump_json())
    logger.debug(f"_course_create_story_agent produced:\n{story.final_output}")
    result = await Runner.run(_course_create_exercise_agent,f"story: '{story.final_output}'; SQL queries: "
                                                            f"'{sample_solutions.model_dump_json()}';")
    logger.debug(f"_course_create_exercise_agent produced:\n{result.final_output.model_dump_json(indent=2)}")
    return result.final_output


# TODO: Check if conditions are fulfilled.
_db_create_tables_agent = Agent(
    name="table generator",
    instructions="""Generate table names for a database to a given topic. 
                 You get a maximum of tables to generate. 
                 Do not use this value as an orientation but decide independently how many tables are necessary to
                 fulfill the following conditions and generate a solution with as few tables as possible:
                 1. It must be reasonable to have at least 5 1-to-many relations, 3
                 many-to-many relation and 2 recursive relation between the tables.
                 2. The generated tables must not be junction tables, even if they do not sound like ones at first glance.
                 3. All data must be german or be loanwords for german language.""",
    model="gpt-6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="high"
        )
    ),
    output_type=DatabaseStructure0
)
"""Agent for generating table names.

The agent is instructed to take into account that the database should have
two 1-to-many relations, one many-to-many-relation and one recursive relation.
"""

async def db_create_tables(topic: str, max_tables: int = MAX_TABLES) -> DatabaseStructure0:
    """Generates tables to a given topic.

    :param topic: Topic for the database.
    :param max_tables: Amount of tables to be generated.
    :return: Generated Tables
    """

    result = await Runner.run(_db_create_tables_agent,
                              f"Generate up to {max_tables} tables for a database with the topic '{topic}'.")
    logger.debug(f"_db_create_tables_agent produced:\n{result.final_output.model_dump_json(indent=2)}")
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
                 All data must be german or be loanwords for german language and follow SQL naming conventions.""",
    model="gpt-6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="xhigh"
        )
    ),
    output_type=DatabaseStructure1
)
"""Agent for generating attributes, used in :func:'db_create_attributes'

The agent is instructed to not generate primary or secondary keys and that the
database should have a table with two integers, a table with two varchar and
a table with one integer and one varchar.
"""

async def db_create_attributes(database: DatabaseStructure0, max_attributes: int = MAX_ATTRIBUTES) -> DatabaseStructure1:
    """Generates attributes for each of a collection of tables for a given topic.

    :param database: Database including topic and table names.
    :param amount_attributes: Amount of attributes to be generated per table.
    :return: Database with generated attributes.
    """

    input_string = f"Generate up to {max_attributes} attributes per table for: {database.model_dump_json()}"
    result = await Runner.run(_db_create_attributes_agent, input_string)
    logger.debug(f"_db_create_attributes_agent produced:\n{result.final_output.model_dump_json(indent=2)}")
    return result.final_output


_db_create_attribute_types_agent = Agent(
    name="attribute type generator",
    instructions="""Generate attribute types for an unfinished database.
                 You are only allowed to use following types: VARCHAR, BOOL, INT, DEC, DATE, DATETIME, TIME and YEAR.
                 The x and y values in the attributes are for the parameters of the type.
                 For example an attribute of type DEC(4, 2) has type=DEC, x=4 and y=2.""",
    model="gpt-6-luna",
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
    model="gpt-6-luna",
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
                 There has to be at least three many-to-many relations, four 1-to-many relations and two recursive relations.
                 You are not allowed to add any table to the database except relation-tables.
                 1-to-many relations are implemented with foreign keys.
                 many-to-many relations are implemented with a relation-tables which need a composite primary key.
                 This is represented with two IDs of type "INT PRIMARY KEY"
                 All data must be german or be loanwords for german language.
                 """,
    model="gpt-6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="high"
        )
    ),
    output_type=DatabaseStructure2
)
"""Agent for generating relations, used in :func:`db_finalize_structure`.

The agent is instructed to generate at leas one many-to-many relation, two
1-to-many relations and one recursive relation.
"""

async def db_finalize_structure(database: DatabaseStructure1) -> DatabaseStructure2:
    """Generates relations and keys for a given database.

    :param database: database with topic and tables including their attributes.
    :return: Database in json format
    """

    result = await Runner.run(_db_create_attribute_types_agent,database.model_dump_json())
    logger.debug(f"_db_create_attribute_types_agent produced:\n{result.final_output.model_dump_json(indent=2)}")
    result = await Runner.run(_db_create_primary_keys_agent, result.final_output.model_dump_json())
    logger.debug(f"_db_create_primary_keys_agent produced:\n{result.final_output.model_dump_json(indent=2)}")
    result = await Runner.run(_db_create_relations_agent, result.final_output.model_dump_json())
    logger.debug(f"_db_create_relations_agent produced:\n{result.final_output.model_dump_json(indent=2)}")
    return result.final_output


_db_fill_agent = Agent(
    name="database filler",
    instructions=f"""Fill an empty database with authentic data.
                 The database should have 300 entries total.
                 The ratio of entries for each table should comply with the ratio in a real database.
                 The database should contain {ORPHANED_MIN} to {ORPHANED_MAX} orphaned records in a 
                 one-to-many relation and a many-to-many relation each.
                 The database should contain {UNREFERENCED_MIN} to {UNREFERRED_MAX} unreferenced records 
                 in a one-to-many relation and a many-to-many relation each.
                 All data must be german or be loanwords for german language.""",
    model="gpt-6-luna",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            context="current_turn",
            effort="high"
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


def _check_databases_exist():
    """Checks if databases.db exists."""

    if not os.path.isfile("databases.db"):
        logger.warning("""'databases.db' does not exist. Run 'create_database.py' to create file and log all databases
                        created with DatabAIse.""")


def namingConventions(s: str) -> str:
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


def removeApostrophes(s: str) -> str:
    """Removes all apostrophes"""

    if type(s) is str:
        return re.sub("[']", "", s)
    else:
        return s


def replaceUmlauts(s: str) -> str:
    """Replaces all german umlauts with transliterations"""

    if type(s) is str:
        return re.sub("[Ä]", "Ae", re.sub("[Ö]", "Oe", re.sub("[Ü]", "Ue", re.sub("[ä]", "ae", re.sub("[ö]", "oe", re.sub("[ü]", "ue", re.sub("[ß]", "ss", s)))))))
    else:
        return s

logger = logger_module.create_logger("")
# Load files
try:
    course_1_db: str = open("course_db/01Kochbuch.sql").read()
    """Database for control group of study for course 1 (cookbook): 
    :doc:`/templates/course_db_1`
    
    :meta hide-value:"""
    course_2_db: str = open("course_db/02Berufsorientierung.sql").read()
    """Database for control group of study for course 2 (career orientation): 
    :doc:`/templates/course_db_2`
    
    :meta hide-value:"""
    course_3_db: str = open("course_db/03Nachbarschafts-Bibliothek.sql").read()
    """Database for control group of study for course 3 (library): 
    :doc:`/templates/course_db_3`
    
    :meta hide-value:"""
    course_4_db: str = open("course_db/04ÖPNV Frankfurt am Main.sql").read()
    """Database for control group of study for course 4 (public transport in Ffm): 
    :doc:`/templates/course_db_4`
    
    :meta hide-value:"""
    course_5_db: str = open("course_db/05Musikarchiv.sql").read()
    """Database for control group of study for course 5 (music archive): 
    :doc:`/templates/course_db_5`
    
    :meta hide-value:"""
    course_6_db: str = open("course_db/06MeilensteineDerWeltgeschichte.sql").read()
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
    pages.build()
