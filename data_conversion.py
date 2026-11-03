import json
import logging
import re

import logger_module
from base_models import DatabaseStructure3, _Table3, _Attribute, Type, _DataEntry

logger = logger_module.create_logger("data_conversion")

def db_structure_3_to_sql(database: DatabaseStructure3) -> str:
    """Converts a DatabaseStructure3 object to a sql string.

    :param database: database with data.
    :return: String of sql statements to create database.
    """

    logger.info("Converting DatabaseStructure3 object to string")
    if logger.getEffectiveLevel() == logging.DEBUG:
        db_without_data = {
            "topic": database.topic,
            "tables": [{
                "name": table.name,
                "attributes": [{
                    "name": attribute.name,
                    "type": attribute.type,
                    "x": attribute.x,
                    "y": attribute.y,
                    "primary_key": attribute.primary_key,
                    "foreign_key": attribute.foreign_key,
                    "foreign_ref_table_name": attribute.foreign_ref_table_name,
                    "foreign_ref_attribute_name": attribute.foreign_ref_attribute_name
                } for attribute in table.attributes]
            } for table in database.tables]
        }
        logger.debug(f"DatabaseStructure3 object:\n{json.dumps(db_without_data, indent=2)}")

    sql_list = []
    sql_list.append(f"CREATE DATABASE '{database.topic}'")
    sql_list.append(f"USE '{database.topic}'")
    logger.debug("Create database")

    entity_tables, junction_tables = database.split_entity_junction_tables()
    _sql_create_entity_tables(entity_tables, sql_list)
    _sql_create_junction_tables(junction_tables, sql_list)
    _sql_insert_data(database.tables, sql_list)

    sql_string = ""
    for sql_command in sql_list:
        sql_string += f"{sql_command};\n"
    return sql_string


def _sql_create_entity_tables(entity_tables: list[_Table3], sql_list: list[str]) -> None:
    logger.debug("Iterate entity tables")
    foreign_key_sets: list[tuple[_Table3, _Attribute, str, str]] = []
    for table in entity_tables:
        sql_list.append(_sql_create_entity_table(table, foreign_key_sets))
    _sql_add_foreign_keys_entity_tables(foreign_key_sets, sql_list)


def _sql_create_entity_table(table: _Table3, foreign_key_sets: list[tuple[_Table3, _Attribute, str, str]]) -> str:
    logger.debug(f"Table '{table.name}'")
    create_table_string = f"CREATE TABLE '{table.name}' ("
    logger.debug("Iterate attributes")
    primary_keys: list[_Attribute] = []
    for attribute in table.attributes:
        create_table_string += f"{_sql_get_attribute(table, attribute, primary_keys, 
                                                     foreign_key_sets, False)}, "
    create_table_string += f"{_sql_get_primary_keys(primary_keys, table.name)})"
    return create_table_string


def _sql_get_primary_keys(primary_keys: list[_Attribute], table_name: str) -> str:
    if len(primary_keys) == 0:
        logger.error(repr(ValueError(f"No primary keys in table {table_name}!")))
    primary_keys_string = "PRIMARY KEY ("
    for primary_key in primary_keys:
        primary_keys_string += f"'{primary_key.name}', "
    primary_keys_string = primary_keys_string[:-2]
    primary_keys_string += ")"
    return primary_keys_string


def _sql_get_attribute(table: _Table3,
                       attribute: _Attribute,
                       primary_keys: list[_Attribute],
                       foreign_key_sets: list[tuple[_Table3, _Attribute, str, str]],
                       add_foreign_keys: bool) -> str:
    logger.debug(f"Attribute '{attribute.name}'")
    if attribute.primary_key:
        primary_keys.append(attribute)
    if attribute.foreign_key:
        ref_table_name = attribute.foreign_ref_table_name if attribute.foreign_ref_table_name else ""
        ref_attribute_name = attribute.foreign_ref_attribute_name if attribute.foreign_ref_attribute_name else ""
        foreign_key_sets.append((table, attribute, ref_table_name, ref_attribute_name))
        if not add_foreign_keys:
            return ""
    attribute_string = f"'{attribute.name}' {attribute.type}"
    if (attribute.type == Type.VARCHAR or attribute.type == Type.INT) and attribute.x is not None:
        attribute_string += f"({attribute.x})"
    elif attribute.type == Type.DEC and attribute.x is not None and attribute.y is not None:
        attribute_string += f"({attribute.x},{attribute.y})"
    return attribute_string



def _sql_add_foreign_keys_entity_tables(foreign_key_sets: list[tuple[_Table3, _Attribute, str, str]],
                                        sql_list: list[str]) -> None:
    logger.debug("Iterate foreign keys of entity tables")
    for (table, attribute, ref_table_name, ref_attribute_name) in foreign_key_sets:
        table.attributes.remove(attribute)
        table.attributes.append(attribute)
        foreign_key_string = (f"ALTER TABLE '{table.name}' ADD COLUMN '{attribute.name}' INT REFERENCES "
                              f"'{ref_table_name}' ('{ref_attribute_name}') DEFERRABLE INITIALLY DEFERRED")
        sql_list.append(foreign_key_string)


def _sql_create_junction_tables(junction_tables: list[_Table3], sql_list: list[str]) -> None:
    logger.debug("Iterate junction tables")
    for table in junction_tables:
        sql_list.append(_sql_create_junction_table(table))


def _sql_create_junction_table(table: _Table3) -> str:
    logger.debug(f"Table '{table.name}'")
    create_table_string = f"CREATE TABLE '{table.name}' ("
    logger.debug("Iterate attributes")
    primary_keys: list[_Attribute] = []
    foreign_key_sets: list[tuple[_Table3, _Attribute, str, str]] = []
    for attribute in table.attributes:
        create_table_string += f"{_sql_get_attribute(table, attribute, primary_keys,
                                                     foreign_key_sets, True)}, "
    create_table_string += f"{_sql_get_primary_keys(primary_keys, table.name)}, "

    for _, attribute, ref_table_name, ref_attribute_name in foreign_key_sets:
        create_table_string += (f"FOREIGN KEY ('{attribute.name}') REFERENCES '{ref_table_name}' "
                                f"('{ref_attribute_name}') DEFERRABLE INITIALLY DEFERRED, ")
    create_table_string = create_table_string[:-2]

    create_table_string += ")"
    return create_table_string


def _sql_insert_data(tables: list[_Table3], sql_list: list[str]) -> None:
    logger.debug("Iterate data entries")
    for table in tables:
        for entry in table.data_entries:
            insert_entry_string = f"INSERT INTO '{table.name}' VALUES ("
            for value in entry.data_points:
                insert_entry_string += f"'{value}', "
            insert_entry_string = insert_entry_string[:-2]
            insert_entry_string += ")"
            sql_list.append(insert_entry_string)







def _db_get_topic(words: list[str], query_pointer: int) -> tuple[str, int]:
    logger.debug("Create database")
    topic = re.sub("'", "", words[2])
    query_pointer += 2
    return topic, query_pointer


def _db_get_tables(tables: list[_Table3], queries: list[str], query_pointer: int) -> int:
    words = queries[query_pointer].split()
    logger.debug("Create table")
    table_name = words[2].replace("'", "")
    logger.debug(f"table name: {table_name}")
    attributes: list[_Attribute] = []

    _db_get_attributes(attributes, words)


    # Get data entries


    # Create table
    table = _Table3(name=table_name, attributes=attributes, data_entries=data_entries)
    tables.append(table)
    return query_pointer


def _db_get_attributes(attributes: list[_Attribute], words: list[str]) -> None:
    logger.debug("Getting attributes")
    word_pointer = 3
    while word_pointer < len(words):
        # Check if primary key or foreign key constraint or attribute
        if words[word_pointer] != "PRIMARY" or words[word_pointer] != "FOREIGN":
            attribute_name = re.sub("['(]", "", words[word_pointer])
            logger.debug(f"Attribute name: {attribute_name}")
            # attribute_full_type is with paremeters. I.e. VARCHAR(255)
            attribute_full_type = words[word_pointer + 1]
            logger.debug(f"Attribute type: {attribute_full_type}")
            attribute_full_type_split = re.split("[(,]", attribute_full_type)
            attribute_full_type_split = [s for s in attribute_full_type_split if s != ""]
            attribute_type_string = attribute_full_type_split[0]
            attribute_type_string = attribute_type_string[:-1] if attribute_type_string.endswith(")") \
                else attribute_type_string
            attribute_type_string = attribute_type_string[:-1] if attribute_type_string.endswith(",") \
                else attribute_type_string
            attribute_type = Type(attribute_type_string)
            attribute_x = None
            attribute_y = None
            if len(attribute_full_type_split) > 1:
                attribute_x_string = re.sub("[^0-9]", "", attribute_full_type_split[1])
                attribute_x = int(attribute_x_string)
            if len(attribute_full_type_split) > 2:
                attribute_y_string = re.sub("[^0-9]", "", attribute_full_type_split[2])
                attribute_y = int(attribute_y_string)
            word_pointer = word_pointer + 2

            # Create attribute
            attribute = _Attribute(name=attribute_name, type=attribute_type, x=attribute_x, y=attribute_y)
            attributes.append(attribute)

        # List of primary keys
        elif words[word_pointer] == "PRIMARY":
            logger.debug(f"Primary Keys: {" ".join(words[word_pointer - len(words):])}")
            word_pointer = word_pointer + 2
            while True:
                attribute_name = re.sub("['();,]", "", words[word_pointer])
                logger.debug(f"Setting attribute '{attribute_name}' as primary key.")
                key_found: bool = False
                for attribute in attributes:
                    if attribute.name == attribute_name:
                        attribute.primary_key = True
                        key_found = True
                        break
                if not key_found:
                    raise ValueError(f"Attribute '{attribute_name}' is listed as primary key but was not found"
                                     f" in attributes:\n{str(attributes)}")
                if words[word_pointer].endswith(";"):
                    word_pointer = word_pointer + 3
                    break
                word_pointer = word_pointer + 1

        # Foreign key of junction table
        else:
            logger.debug(f"Foreign key {words[word_pointer + 2]}")
            attribute_name = re.sub("['()]", "", words[word_pointer + 2])
            ref_table_name = re.sub("[()]", "", words[word_pointer + 4])
            ref_attribute_name = re.sub("['()]", "", words[word_pointer + 5])
            attribute = next(attribute for attribute in attributes if attribute.name == attribute_name)
            attribute.foreign_key = True
            attribute.foreign_ref_table_name = ref_table_name
            attribute.foreign_ref_attribute_name = ref_attribute_name
            word_pointer = word_pointer + 9


def _db_get_data_entries():
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
        data_point_words: list[str] = []
        pointer_is_inside_string: bool = False
        for word_pointer in range(4, len(words)):
            word = words[word_pointer]
            if not pointer_is_inside_string:
                data_point_words = []
                word = word[1:] if word.startswith("(") else word
                if not word.startswith("'"):
                    raise ValueError(f"Expected {word} to be start of a data point but did not start with "
                                     f"single quote")
                word = word[1:]
                if not word.endswith("'"):
                    pointer_is_inside_string = True

            word = word[:-2] if word.endswith("');") else word[:-1] if word.endswith("',") else word
            if word.endswith("'"):
                word = word[:-1]
                pointer_is_inside_string = False

            data_point_words.append(word)
            if not pointer_is_inside_string:
                data_points.append(" ".join(data_point_words))

        # Create data entry
        data_entry = _DataEntry(data_points=data_points)
        data_entries.append(data_entry)


def _db_get_entity_tables_foreign_keys(tables: list[_Table3], words: list[str], query_pointer: int) -> int:
    table_name = words[2].replace("'", "")
    attribute_name = words[5].replace("'", "")



    ref_table_name, ref_attribute_name = words[9].split("(")
    ref_table_name = ref_table_name.replace("'", "")
    ref_attribute_name = re.sub("[');]", "", ref_attribute_name)

    ref_table = None
    ref_attribute = None
    for table in tables:
        if table.name == ref_table_name:
            for attribute in table.attributes:
                if attribute.name == ref_attribute_name:
                    ref_table = table
                    ref_attribute = attribute
                    break
    if ref_table is None or ref_attribute is None:
        raise ValueError(f"Referenced table {ref_table_name} or referenced attribute "
                         f"{ref_attribute_name} not found")

    foreign_key_found: bool = False
    for table in tables:
        if table.name == table_name:
            for attribute in table.attributes:
                if attribute.name == attribute_name:
                    attribute.foreign_ref_table_name = ref_table_name
                    attribute.foreign_ref_attribute_name = ref_attribute_name
                    attribute.foreign_key = True
                    foreign_key_found = True
                    break
    if not foreign_key_found:
        raise ValueError(f"Attribute {attribute_name} of table {table_name} should be foreign key but does not "
                         f"exist.")
    return query_pointer + 1


def sql_to_db_structure_3(sql_string: str, disable_debug: bool = True) -> DatabaseStructure3:
    """Converts a sql string to a DatababaseStructure3 object.

    .. role:: sql(code)
        :language: sql

    :param sql_string:
        | Must have exact format (Including spaces before parentheses!):
        | :sql:`CREATE DATABASE db_name;`
        | :sql:`USE db_name;`
        | :sql:`CREATE TABLE table_1 (List of Attributes, PRIMARY KEYS (List of Primary Keys));`
        | :sql:`INSERT INTO table_1 VALUES (dataset_1);`
        | ...
        | :sql:`INSERT INTO table_1 VALUES (dataset_n);`
        | ...
        | :sql:`CREATE TABLE table_n(Attributes);`
        | :sql:`INSERT INTO table_n VALUES (dataset_1);`
        | ...
        | :sql:`INSERT INTO table_n VALUES (dataset_n);`
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

    queries = sql_string.splitlines()
    query_pointer: int = 0
    while query_pointer < len(queries):
        query = queries[query_pointer]
        logger.debug(f"Query: {query}")
        words = query.split()

        if words[0] == "CREATE" and words[1] == "DATABASE":
            topic, query_pointer = _db_get_topic(words, query_pointer)
        elif words[0] == "CREATE" and words[1] == "TABLE":
            query_pointer = _db_get_tables(tables, queries, query_pointer)
        elif words[0] == "ALTER" and words[1] == "TABLE":
            query_pointer = _db_get_entity_tables_foreign_keys()
        else:
            raise ValueError(f'Unknown query schema:\n"{query}"')

    database = DatabaseStructure3(topic=topic, tables=tables)
    logger.info("Finished conversion.")

    if logger_level_changed:
        logger.setLevel(logger_level)

    return database