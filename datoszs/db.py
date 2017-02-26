from urllib.parse import urlparse
import os
import psycopg2


def connection(connection_url=None):
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
