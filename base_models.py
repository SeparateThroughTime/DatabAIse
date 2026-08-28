"""Module for all BaseModels that are used for structured AI output.

The private classes are not strict private. They are not meant to be used as standalone, but sometimes it
is necessary to instantiate them to instantiate a DatabaseStructureX class.
"""

from enum import StrEnum
from pydantic import BaseModel


class Course(BaseModel):
    """BaseModel for Courses.

    :ivar story: Underlying story for the course.
    :ivar exercises: List of exercises.
    """

    story: str
    exercises: list[str]


class _Solution(BaseModel):
    """BaseModel for single exercise solutions with 'text' boolean to indicate
    complexity of the exercise.

    Abstract and concrete solutions can both use this model.

    :ivar sql_query: Query of exercise.
    :ivar text:
        Boolean to indicate complexity of the exercise. See
        :doc:`/templates/course_templates` for more information.
    """

    sql_query: str
    text: bool

class CourseTemplate(BaseModel):
    """BaseModel for course templates.

    Abstract templates and concrete templates (sample solutions) can both use
    this model.

    :ivar exercise_solutions: List of exercise solutions.
    """

    exercise_solutions: list[_Solution]


class _DataEntry(BaseModel):
    """BaseModel for data entries.

    :ivar data_points: List of data points.
    """

    data_points: list[str]


class Type(StrEnum):
    """Enum with all allowed datatypes for the database."""

    VARCHAR = "VARCHAR"
    TEXT = "TEXT"
    BOOL = "BOOL"
    INT = "INT"
    DEC = "DEC"
    DATE = "DATE"
    DATETIME = "DATETIME"
    TIME = "TIME"
    YEAR = "YEAR"
    INT_PRIMARY_KEY = "INT PRIMARY KEY"


class _Attribute(BaseModel):
    """BaseModel for attributes.

    :ivar name: Name of the attribute.
    :ivar type: Type of the attribute.
    :ivar x: First optional parameter for the type.
    :ivar y: Second optional parameter for the type.
    """

    name: str
    type: Type
    x: int | None
    y: int | None


class _Table1(BaseModel):
    """BaseModel for tables with only there attribute names.

    :ivar name: Name of the table.
    :ivar attributes: List of attribute names.
    """

    name: str
    attributes: list[str]


class _Table2(_Table1):
    """BaseModel for tables with full attributes.

    :ivar attributes: List of attributes.
    """

    attributes: list[_Attribute]


class _Table3(_Table2):
    """BaseModel for tables with data.

    :ivar data_entries: List of data entries.
    """

    data_entries: list[_DataEntry]


class DatabaseStructure0(BaseModel):
    """BaseModel for first step where AI only generates table names.

    :ivar topic: Topic of the database.
    :ivar tables: List of table names."""
    topic: str
    tables: list[str]


class DatabaseStructure1(BaseModel):
    """BaseModel for second step where AI generates attribute names.

    :ivar topic: Topic of the database.
    :ivar tables: List of tables.
    """

    topic: str
    tables: list[_Table1]


class DatabaseStructure2(BaseModel):
    """BaseModel for a database structure without data.

    :ivar topic: Topic of the database.
    :ivar tables: List of tables.
    """

    topic: str
    tables: list[_Table2]


class DatabaseStructure3(BaseModel):
    """Basemodel for database with data.

    :ivar topic: Topic of the database.
    :ivar tables: List of tables.
    """

    topic: str
    tables: list[_Table3]
