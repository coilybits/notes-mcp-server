from enum import Enum


class NoteExistsException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class NoteNotExistsException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class Query:
    NOTE_TABLE = "notes"
    GET_NOTE = f"SELECT name, description FROM {NOTE_TABLE} WHERE name=?"
    REMOVE_NOTE = f"DELETE FROM {NOTE_TABLE} WHERE name=?"
    GET_NOTES = f"SELECT name, description FROM {NOTE_TABLE}"
    INSERT_NOTE = f"INSERT INTO {NOTE_TABLE}(name, description) VALUES(?, ?)"
    CREATE_NOTE_META = f"""CREATE TABLE IF NOT EXISTS {NOTE_TABLE} (
        name CHAR(24) PRIMARY KEY,
        description VARCHAR
    )"""


class Tools(str, Enum):
    REMOVE_NOTE = "remove-note"
    CREATE_NOTE = "create-note"
