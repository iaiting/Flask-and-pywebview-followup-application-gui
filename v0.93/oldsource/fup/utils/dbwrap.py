def connection():
    #Connect to a db and if it not exists creates one with the name given
    import sqlite3
    from fup.utils.jsoninfo import configInfo
    config = configInfo()
    dbNamePath = config["path_to_database"]
    try:
        connection = sqlite3.connect(dbNamePath)
        #cursor = connection.cursor()
        return connection
    except:
        return False


def execute_query(query, keepConn=False):
    #Execute query, commit and close query
    from fup.utils.dbwrap import connection
    try:#execute query in database
        conn = connection()
        if conn == False:
            print("Connection to db failed")
            return False #if conn fails
        else:
            with conn:
                conn.execute(query)
            if keepConn:
                return True
            else:
                conn.close()
                return True
    except Exception as e:#query was not executed, Try again
        print("Got error: ",e)
        return False


def get_dftable(table_name):
    #gets the table from the db
    from fup.utils.dbwrap import connection
    import pandas as pd
    conn = connection()
    query = "SELECT * FROM {}".format(table_name)
    df = pd.read_sql_query(query, conn)
    return df


def update_tbcell(table_name, coltoUpdate, colValtoUpdate, colID, rowID):
    from fup.utils.dbwrap import execute_query

    update_batch = """UPDATE "{}" SET "{}"="{}" WHERE "{}"="{}";""".format(table_name, coltoUpdate, colValtoUpdate, colID, rowID)
    if execute_query(update_batch) == True:
        return True
    else:
        return False


def tb_cols_placeholder(tableName):
    #Get the column names and make placeholders for them
    from fup.utils.dbwrap import get_dftable
    import pandas as pd
    df = get_dftable(tableName)
    colsname = tuple(df.columns.tolist())
    phli = []
    for n in range(len(colsname)):
        phli.append('{}')

    emptyplaceholders = tuple(phli)
    colsphdict = {"columns": colsname, "placeholders": emptyplaceholders}

    return colsphdict


def sql_updateDict(tableName, updatedict, colIDName):
    from fup.utils.dbwrap import execute_query

    colsvals = []
    for col, val in updatedict.items():
        if col != colIDName:
            sqval = col + '=' + "'{}'".format(val)
            colsvals.append(sqval)
        else:
            whereCol_value = col + '=' + "'{}'".format(val)

    colstoUpdate = ', '.join(colsvals)

    sql_update = str("UPDATE " + '{}'.format(tableName) + " SET " + colstoUpdate + " WHERE " + whereCol_value + ";")
   
    return execute_query(sql_update)


def sql_insertDict(tableName, infoaddDict):
    from fup.utils.dbwrap import execute_query

    processedInfo = {}
    for k, val in infoaddDict.items():
        if isinstance(val, str):
            templi = []
            templi.append(val)
            val = [str(v) for v in templi]
            processedInfo[k] = ','.join(list(set(val)))
        else:
            try:
                val = [str(v) for v in val]
                processedInfo[k] = ','.join(list(set(val)))
            except:
                processedInfo[k] = str(val)

    columns = tuple(processedInfo.keys())
    values = tuple(processedInfo.values())

    sql_insert = """INSERT INTO {} {} VALUES {};"""
    insert = sql_insert.format(tableName, columns, values)
    #print(insert)

    return execute_query(insert)


def sql_deleteRow(table, colID, rowID):
    from fup.utils.dbwrap import execute_query
    delete_row = """DELETE FROM {} WHERE {}='{}' """.format(table, colID, rowID)
    return execute_query(delete_row)



def prepcell(cell, tolist=False):
    #Remove whitespaces/new line from the string and put words to list if needed
    cell = str(cell).strip().replace('\n', ' ') # using replace to avoid POST\n156424 > POST156424
    cellli = ''.join(cell).split(' ')
    cellli = [c.strip() for c in cellli if len(c) != 0]

    if tolist:
        return cellli
    else:
        cellstr = ' '.join(cellli)
    return cellstr


def stringifyDF(df):
    #Clean cells and make all columns astype string
    from fup.utils.dbwrap import prepcell
    import pandas as pd

    columnsli = df.columns.tolist()
    for col in columnsli:
        df[col] = df[col].apply(lambda cell: prepcell(cell))
    return df


def df2sql(df, dfname, stringify=False):
    import pandas as pd
    from fup.utils.dbwrap import stringifyDF, connection
    connection = connection()
    if connection == False:
        print("Connection to db failed")

    if stringify:
        df = stringifyDF(df)
        
    df.to_sql(dfname, connection, if_exists="replace", index=False)
    connection.commit()


def sql2df(table_name):
    import pandas as pd
    from fup.utils.dbwrap import connection
    connection = connection()
    if connection == False:
        print("Connection to db failed")

    query = "SELECT * FROM {}".format(table_name)
    df = pd.read_sql_query(query, connection)
    return df















#
