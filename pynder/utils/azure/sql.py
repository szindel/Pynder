import pyodbc
import pandas as pd


def cnxn_string_to_dict(cnxn_string):
    """Function to convert SQL connection string key=value to dictionary.

    :param cnxn_string: connection strong
    :return: dict
    """
    my_dict = {}
    for line in cnxn_string.split(";"):
        if "=" in line:
            key, value = line.split("=")
            my_dict[key.lower()] = value
    return my_dict


def getSqlConnectionObject(cnxn_string, driver="ODBC Driver 17 for SQL Server"):
    """Function to return a ODBC connection object from a connection string

    :param cnxn_string: connection string
    :return: ODBC connection object
    """
    dict_cnxn = cnxn_string_to_dict(cnxn_string)

    # we did Lower on the keys so therefore
    databaseName = dict_cnxn["initial catalog"]
    databaseUserName = dict_cnxn["user id"]
    server = dict_cnxn["server"].split(",")[0]
    password = dict_cnxn["password"]

    connectionString = "DRIVER={driver};SERVER={server};PORT=1433;DATABASE={databaseName};UID={databaseUserName};PWD={password}".format(
        driver=driver,
        server=server,
        databaseName=databaseName,
        databaseUserName=databaseUserName,
        password=password,
    )
    try:
        cnxn = pyodbc.connect(connectionString)

    except (pyodbc.Error, pyodbc.InterfaceError) as e:
        print("Logging failed")
        raise e

    else:
        return cnxn, dict_cnxn


def insert_into_sql_table(connection_string, values, cols, table):
    """Function to insert single value in a sql table

    :param connection_string: str
    :param value: tuple
    :param col: tuple
    :param table: str
    :return: None
    """
    cnxn, dict_cnxn = getSqlConnectionObject(connection_string)
    assert cnxn, "Please provide a valid SQL connection"

    assert isinstance(values, tuple)
    assert isinstance(cols, tuple)
    assert isinstance(table, str)

    # we need to remove the string quotations for the sql query
    cols = str(cols).replace("'", "").replace('"', '"')
    query = f"INSERT INTO {table} {cols} VALUES {values}"
    try:
        print(f"Info - inserting into {table} on sql server")
        print(query)
        cursor = cnxn.cursor()
        cursor.execute(query)
        cursor.commit()
    except (pyodbc.ProgrammingError, pd.io.sql.DatabaseError):
        raise (f"Error while running {query}")
    finally:
        cnxn.close()
        return None


def run_query(connection_string, query):
    """Function to get a table from the connection string

    :param connection_string: str
    :param table: str
    :param n_rows: str
    :return: pd.DataFrame
    """
    cnxn, dict_cnxn = getSqlConnectionObject(
        connection_string, driver="ODBC Driver 17 for SQL Server"
    )

    assert cnxn, "Please provide a valid SQL connection"

    try:
        print(f"Info - Running query on sql server")
        df = pd.read_sql_query(query, cnxn)
        if df.empty:
            print(f"Warning - Empty dataframe fetched from SQL: {query}")
    except (pyodbc.ProgrammingError, pd.io.sql.DatabaseError):
        raise (f"Error while running {query}")
    else:
        cnxn.close()
        return df


def get_table_sql(connection_string, table=None, n_rows="*"):
    """Function to get a table from the connection string

    :param connection_string: str
    :param table: str
    :param n_rows: str
    :return: pd.DataFrame
    """
    cnxn, dict_cnxn = getSqlConnectionObject(connection_string)

    assert cnxn, "Please provide a valid SQL connection"
    assert table, "Please provide a valid SQL table name"

    try:
        print(f"Info - Fetching SQL table: {table}")
        df = pd.read_sql_query(f"SELECT {n_rows} FROM {table}", cnxn)
        assert not df.empty, f"Empty dataframe from {table} fetched from SQL."
    except (pyodbc.ProgrammingError, pd.io.sql.DatabaseError):
        raise (f"Error while getting {table}")
    else:
        cnxn.close()
        return df


def get_row_from_sql_table(
    connection_string, cols, table, col_id, val_id, bWildcard_search=False
):
    """Function that fetches a row from a table with wildcard option

    :param connection_string:
    :param cols:
    :param table:
    :param col_id:
    :param val_id:
    :return:
    """
    assert isinstance(cols, tuple)

    # if val is a string, place sql string qoutations around it.
    if isinstance(val_id, str):
        if not val_id[0] == "'":
            val_id = "'" + val_id
        if not val_id[-1] == "'":
            val_id = val_id + "'"

    if bWildcard_search:
        # add wildcard to start of source
        val_id = val_id[0] + "%" + val_id[1:]
        query = (
            f"""SELECT {", ".join(cols)} FROM {table} WHERE {col_id} LIKE {val_id}"""
        )
    else:
        query = f"""SELECT {", ".join(cols)} FROM {table} WHERE {col_id} = {val_id}"""

    res = run_query(connection_string, query=query)

    if res.empty:
        print(f"No results queried from SQL: {res}")
        return [None] * len(cols)
    # check on rows
    assert res.shape[0] == 1, f"ID not unique: more than 1 row found in table: {table}"
    # check on n returned items
    assert res.shape[1] == len(
        cols
    ), f"more cols returned:{res.columns} than requested: {cols}"

    if len(cols) == 1:
        return res.loc[0, cols[0]]
    else:
        return [res.loc[0, c] for c in cols]


def update_sql_table_by_row_id(connection_string, value, table, _id, col, col_id):
    """Function update rows in a sql table by id

    :param connection_string: str
    :param value: str/number
    :param table: str
    :param col: str
    :param row_id: int
    :return: None
    """
    cnxn, dict_cnxn = getSqlConnectionObject(connection_string)
    assert cnxn, "Please provide a valid SQL connection"

    if isinstance(value, str):
        value = f"'{value}'"

    query = f"UPDATE {table} SET {col} = {value} WHERE {col_id}={_id};"
    try:
        print(f"Info - Running query on sql server")
        cursor = cnxn.cursor()
        cursor.execute(query)
        cursor.commit()
    except (pyodbc.ProgrammingError, pd.io.sql.DatabaseError):
        raise (f"Error while running {query}")
    else:
        cnxn.close()
        return None
