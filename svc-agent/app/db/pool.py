import os

from pgvector.psycopg import register_vector
from psycopg_pool import ConnectionPool


def configure_connection(conn):
    register_vector(conn)


conn_str = (
    f"postgresql://{os.getenv('VDB_USER')}:"
    f"{os.getenv('VDB_PASSWORD')}@"
    f"{os.getenv('VDB_HOST')}:"
    f"{os.getenv('VDB_PORT')}/"
    f"{os.getenv('VDB')}"
)


pool = ConnectionPool(
    conninfo=conn_str,
    min_size=1,
    max_size=5,
    timeout=30,
    max_idle=300,
    open=False,
    configure=configure_connection
)

pool.open()
pool.wait()
