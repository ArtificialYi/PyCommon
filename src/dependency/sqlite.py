import sqlite3


def dict_factory(cursor: sqlite3.Cursor, row):  # pragma: no cover
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
