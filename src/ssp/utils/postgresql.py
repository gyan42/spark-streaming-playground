#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import psycopg2
import pandas as pd

def postgressql_connection(host, port, database, user, password):
    conn = psycopg2.connect(host=host, port=port, database=database, user=user, password=password)
    return conn

def create_pandas_table(sql_query, database_connection):
    # A function that takes in a PostgreSQL query and outputs a pandas database
    # Create a new cursor
    cur = database_connection.cursor()
    table = pd.read_sql_query(sql_query, database_connection)
    cur.close()
    return table

def close_connection(database_connection):
    database_connection.close()