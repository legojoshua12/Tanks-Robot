import psycopg2
import os
from psycopg2 import pool
from typing import Union, List


class ConnectionPool:
    _connection_pool = None

    @staticmethod
    def get_instance():
        if ConnectionPool._connection_pool is None:
            ConnectionPool._connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT')
            )
        return ConnectionPool._connection_pool


def query_database(connection, instruction: str, *args) -> Union[List, None]:
    """Performs an instruction on the database
    :param connection: Connection object to database
    :param instruction: Raw SQL statement executed on the database
    :param args: Optional arguments for the SQL query
    :return: A list of the SQL response data or None if no return
    """
    try:
        cursor = connection.cursor()
        cursor.execute(instruction, args)
        connection.commit()
        result = cursor.fetchall()
        if len(result) < 1 or result is None:
            return None
        return result
    except Exception as _:
        connection.rollback()
        return None
    finally:
        cursor.close()
