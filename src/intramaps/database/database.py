'''Database class definition.'''
import sqlite3
from pathlib import Path

class Database:
    '''SQLite connection shared with all repositories.
    
    Attributes:
        connection: sqlite3 database connection.
    
    '''

    SCHEMA_PATH = Path(__file__).with_name("schema.sql")

    def __init__(self, database_path = "data/intramaps.db"):
        self.__connection = sqlite3.connect(database_path)
        self.__connection.execute("PRAGMA foreign_keys = ON")
        self.__connection.row_factory = sqlite3.Row

    def create_schema(self):
        '''Creates new database schema. If already exists, keep previous one.'''
        with open(self.SCHEMA_PATH,"r", encoding="utf-8") as f:
            self.__connection.executescript(f.read())

    def execute(self, sql, params = tuple()):
        '''Executes a write statement and commits it.

        Args:
            sql: SQL statement, with "?" where the values go.
            params: Values for the "?" placeholders, in the same order.

        Returns:
            Cursor object.
        '''
        cursor = self.__connection.execute(sql, params)
        self.__connection.commit()
        return cursor

    def fetch(self, sql, params = tuple(), count:int = -1):
        '''Executes a SELECT and returns up to count rows.

        Args:
            sql: SELECT statement, with "?" where the values go.
            params: Values for the "?" placeholders, in the same order.
            count: number of rows, default [-1] returns all rows.

        Returns:
            The first count rows, readable by column name, or [] if there is no match.
        '''
        cursor = self.__connection.execute(sql, params)
        return cursor.fetchmany(count)

    def close(self):
        '''Closes the database connection.'''
        self.__connection.close()
