from threading import currentThread
from urllib.parse import urlparse
import os
import psycopg2
import spiderpig as sp


_GLOBAL_CONNECTION = {}


class global_connection:

    def __enter__(self):
        _GLOBAL_CONNECTION[currentThread()] = create_connection()

    def __exit__(self, exc_type, exc_value, traceback):
        connection = _GLOBAL_CONNECTION[currentThread()]
        del _GLOBAL_CONNECTION[currentThread()]
        connection.close()


def connection():
    return _GLOBAL_CONNECTION[currentThread()]


@sp.configured()
def create_connection(connection_url=None):
    if connection_url is None:
        connection_url = os.environ.get('DATABASE_URL')
    if not connection_url:
        raise Exception('The database connection is not configured')
    config = urlparse(connection_url)
    return psycopg2.connect(
        database=config.path[1:],
        user=config.username,
        password=config.password,
        host=config.hostname
    )
