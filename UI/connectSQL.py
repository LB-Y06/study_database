"""SQL Server connection settings loaded from environment variables."""

import os

import pyodbc


server = os.getenv("OLPMS_SERVER", "localhost")
database = os.getenv("OLPMS_DATABASE", "OLPMS")
username = os.getenv("OLPMS_USERNAME", "sa")
password = os.getenv("OLPMS_PASSWORD", "")
driver = os.getenv("OLPMS_DRIVER", "ODBC Driver 17 for SQL Server")

if not password:
    raise RuntimeError(
        "Set OLPMS_PASSWORD before starting the application. "
        "See README.md for the PowerShell example."
    )

connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password}"
)

connection = pyodbc.connect(connection_string)
cursor = connection.cursor()


