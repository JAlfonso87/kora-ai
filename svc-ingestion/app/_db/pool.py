import os
from psycopg_pool import ConnectionPool
from pgvector.psycopg import register_vector

conn_str = f"postgresql://{os.getenv('VDB_USER')}:{os.getenv('VDB_PASSWORD')}@{os.getenv('VDB_HOST')}:{os.getenv('VDB_PORT')}/{os.getenv('VDB')}"


def configure_connection(conn):
    register_vector(conn)

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