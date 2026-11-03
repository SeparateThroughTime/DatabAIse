"""Module for all BaseModels that are used for structured AI output.

The private classes are not strict private. They are not meant to be used as standalone, but sometimes it
is necessary to instantiate them to instantiate a DatabaseStructureX class.
"""

from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


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

    data_points: list[str] = Field(
        description="One value for each table attribute, in the same order as the attributes."
    )


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


class _Attribute(BaseModel):
    """BaseModel for attributes.

    :ivar name: Name of the attribute.
    :ivar type: Type of the attribute.
    :ivar x: First optional parameter for the type.
    :ivar y: Second optional parameter for the type.
    :ivar primary_key: Optional bool to indicate primary keys
    :ivar foreign_ref: Optional tuple to reference table and attribute of foreign key.
    """

    name: str
    type: Type
    x: Optional[int] = None
    y: Optional[int] = None
    primary_key: bool = False
    foreign_key: bool = False
    foreign_ref_table_name: Optional[str] = None
    foreign_ref_attribute_name: Optional[str] = None


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

    attributes: list[_Attribute] = Field(
        description=(
            "The table attributes. Every data entry must contain exactly one value "
            "for each attribute, in this order."
        )
    )

    def get_primary_key_indices(self) -> list[int]:
        return [i for i, attribute in enumerate(self.attributes) if attribute.primary_key]


    def get_foreign_key_indices(self) -> list[int]:
        return[i for i, attribute in enumerate(self.attributes) if attribute.foreign_key]


    def get_attribute_index(self, attribute_name: str) -> int:
        return next(i for i in range(len(self.attributes)) if self.attributes[i].name == attribute_name)


class _Table3(_Table2):
    """BaseModel for tables with data.

    :ivar data_entries: List of data entries.
    """

    data_entries: list[_DataEntry]

    @model_validator(mode="after")
    def validate_data_entry_len(self) -> "_Table3":
        attribute_count = len(self.attributes)
        for index, entry in enumerate(self.data_entries):
            if len(entry.data_points) != attribute_count:
                raise ValueError(
                    f"data_entries[{index}] has {len(entry.data_points)} values, "
                    f"but table {self.name!r} has {attribute_count} attributes"
                )
        return self


    def get_column(self, index: int) ->  list[str]:
        return [entry.data_points[index] for entry in self.data_entries]


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


ORPHANED_MIN = 3
ORPHANED_MAX = 5
UNREFERENCED_MIN = 2
UNREFERRED_MAX = 3

class DatabaseStructure3(BaseModel):
    """Basemodel for database with data.

    :ivar topic: Topic of the database.
    :ivar tables: List of tables.
    """

    topic: str
    tables: list[_Table3]

    @model_validator(mode="after")
    def validate_stray_records(self) -> "DatabaseStructure3":
        entity_tables, junction_tables = self.split_entity_junction_tables()
        one_many_orphaned, one_many_unreferenced = self._count_stray_records(entity_tables)
        many_many_orphaned, many_many_unreferenced = self._count_stray_records(junction_tables)

        exceptions = [val_exc for val_exc, condition in [
            (ValueError(f"Only {one_many_orphaned} orphaned records found in one-to-many relations. "
                       f"{ORPHANED_MIN} are expected."),
            one_many_orphaned < ORPHANED_MIN),
            (ValueError(f"Only {many_many_orphaned} orphaned records found in many-to-many relations. "
                       f"{ORPHANED_MIN} are expected."),
            many_many_orphaned < ORPHANED_MIN),
            (ValueError(f"Only {one_many_unreferenced} unreferenced records found in one-to-many relations. "
                       f"{UNREFERENCED_MIN} are expected."),
            one_many_unreferenced < UNREFERENCED_MIN),
            (ValueError(f"Only {one_many_orphaned} unreferenced records found in many-to-many relations. "
                       f"{UNREFERENCED_MIN} are expected."),
            many_many_unreferenced < UNREFERENCED_MIN)]
                      if condition]
        if exceptions:
            raise ExceptionGroup("One or more errors depending stray record validation occurred.", exceptions)

        return self


    def split_entity_junction_tables(self) -> tuple[list[_Table3], list[_Table3]]:
        entity_tables: list[_Table3] = []
        junction_tables: list[_Table3] = []
        for table in self.tables:
            primary_foreign_key_counter = 0
            for attribute in table.attributes:
                if attribute.primary_key and attribute.foreign_key:
                    primary_foreign_key_counter += 1
            if primary_foreign_key_counter >= 1:
                junction_tables.append(table)
            else:
                entity_tables.append(table)
        return entity_tables, junction_tables


    def _count_stray_records(self, table_selection: list[_Table3]) -> tuple[int, int]:
        orphaned = 0
        unreferenced = 0
        for table in table_selection:
            for foreign_key_index in table.get_foreign_key_indices():
                foreign_keys = table.get_column(foreign_key_index)
                # noinspection bad-argument-type
                ref_table = self.get_table(table.attributes[foreign_key_index].foreign_ref_table_name)
                ref_attribute_name = table.attributes[foreign_key_index].foreign_ref_attribute_name
                # noinspection bad-argument-type
                ref_ids = ref_table.get_column(ref_table.get_attribute_index(ref_attribute_name))
                for foreign_key in foreign_keys:
                    if foreign_key not in ref_ids:
                        orphaned += 1
                for referenced_id in ref_ids:
                    if referenced_id not in foreign_keys:
                        unreferenced += 1
        return orphaned, unreferenced


    def get_table(self, table_name: str) -> _Table3:
        return next(table for table in self.tables if table.name == table_name)
