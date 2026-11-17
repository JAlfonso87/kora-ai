
import os
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from psycopg_pool import ConnectionPool


load_dotenv()


def configure_connection(conn):
    register_vector(conn)

required_variables = [
    "VDB_USER",
    "VDB_PASSWORD",
    "VDB_HOST",
    "VDB_PORT",
    "VDB"
]

missing_variables = [
    variable for variable in required_variables
    if not os.getenv(variable)
]

if missing_variables:
    raise ValueError(
        f"Faltan variables de entorno: {', '.join(missing_variables)}"
    )


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
