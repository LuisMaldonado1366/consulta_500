# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# connection.py

"""
Description: Custom python module to interact with mysql databases.
Author: Luis Maldonado
Created on: Thu Aug 31 14:24:05 2023
Modified on: Thu June  13 12:53:36 2024
Version: 2.0.0
Dependencies: pandas, mysql.connector.
"""


################################## Libraries ##################################
# Third party.
import pandas as pd
from mysql.connector import Error, connect


################################### Classes ###################################
class Connection:
    """
    A class for connection and managment of a mysql database.

    Attributes:
        __host (str): Host name for the database.
        __user (str): User name of the database.
        __password (str): Password for the user.
        __connection (mysql.connector): Object for the mysql connection.
        __databse (str): Database name.
        __cursor (mysql.cursor): Object to execute queries on mysql connection.
        __fields (array): Fields to operate into the sql query.
    """

    def __init__(self, host: str = 'localhost', port: int = 3306,
                 user: str = 'root', password: str = '',
                 database: str = None) -> None:
        """
        Resume: Class constructor.
        Description: Creates an object of the class associating the database
            credentials.
        Args:
            host (str): Host name for the database connection.
            user (str): User name of the database.
            password (str): Password for the user name.
           
        Returns:
            None
        """
        self.__host = host
        self.__user = user
        self.__password = password
        self.__connection = None
        self.__database = database
        self.__cursor = None
        self.__fields = []
        self.__port = port


    def set_credentials(self, user: str, password: str) -> None:
        """
        Resume: Set the connection credentials.
        Description: Update the connection credentials if needed (not recommended).
        Args:
            user (str): User name of the database.
            password (str): Password for the user name.
           
        Returns:
            None
        """
        self.__user = user
        self.__password = password


    def __connect(self) -> object:
        """
        Resume: Establishes the connection to the database.
        Description: Creates an object connector to interact with the database.
        Args:
            None
            
        Returns:
            mysql.connector: The created connection associated with the database.
        """
        try:
            self.__connection = connect(
                host = self.__host,
                port = self.__port,
                user = self.__user,
                password = self.__password,
                db = self.__database
            )

        except Error as ex:
            print(f'Error on connect: {format(ex)}')

        return self.__connection


    def __create_cursor(self) -> object:
        """
        Resume: Creates a cursor object to execute the queries.
        Description: Creates a cursor object to manipulate the sql queries.
        Args:
            database (str): Database name.
            
        Returns:
            None
        """
        _connection = self.__connect()
        self.__cursor = _connection.cursor()

        return self.__cursor


    def fetch_data(self, table: str, **kwargs: list) -> pd.DataFrame:
        """
        Resume: Retrieves the specified data table from the given database.
        Description: Retrieves the specified data from a selected table within
            the database, if the query fields are specified within the keyword
            arguments, it brings just those by putting it in the select statement,
            otherwise it brings all the available fields in the table.
        Args:
            database (str): Database name to connecto to.
            table (str): Table name to fetch the data from.
            **kwargs: Additional keyword arguments:
                - fields (list): A list of column names to retrieve from the table.
            
        Returns:
            pandas.DataFrame: The retrieved data formated as a pandas dataframe.
        """
        _table = table
        self.__cursor = self.__create_cursor()

        _str_query = 'SELECT '

        if 'fields' in kwargs:
            self.__fields = kwargs['fields']
            for field in self.__fields:
                _str_query += field + ', '
            _str_query = _str_query[:-2]
        else:
            _str_query += '*'

        _str_query += ' FROM ' + _table
        
        if 'filter_query' in kwargs:
            _str_query += f" {kwargs['filter_query']}"

        self.__cursor.execute(_str_query)

        _results = self.__cursor.fetchall()

        _result_df = pd.DataFrame(data = _results, columns = self.__cursor.column_names)

        self.__connection.close()
        self.__cursor.close()

        return _result_df


    def insert_data(self, table: str, data_df: pd.DataFrame) -> bool:
        """
        Resume: Inserts the given data to the specified table from the given database.
        Description: Writes the given data to a table in the database. If the key value
            is not present within the table, the data is inserted, otherwise, the data
            is updated in the duplicated register.
        Args:
            database (str): Database name to connecto to.
            table (str): Table name to fetch the data from.
            data_df (pandas.DataFrame): Data to be inserted/updated within the table.
            
        Returns:
            bool: True if the insertion was succesful, False otherwise.
        """
        try:
            self.__cursor = self.__create_cursor()
            self.__fields = str(list(data_df.columns)).\
                translate(str.maketrans({'[': '(', ']': ')'}))
            self.__fields = self.__fields.replace("'", "")
            _str_query_complement = ''
            for field in range(len(data_df.columns)):
                _str_query_complement += '%s, '
            _str_query_complement = _str_query_complement[:-2]

            _values = []

            for index in range(data_df.shape[0]):
                var = []
                for col in data_df.columns:
                    if data_df.iloc[index][col] is None:
                        temp_var = None
                    elif isinstance(data_df.iloc[index][col], int):
                        temp_var = int(data_df.iloc[index][col])
                    else:
                        temp_var = str(data_df.iloc[index][col])
                    var.append(temp_var)
                _values.append(tuple(var))

            _str_query_values = ''
            for field in data_df.columns:
                _str_query_values += f'{field} = VALUES({field}), '
            _str_query_values = _str_query_values[:-2]

            _str_query = (f"INSERT INTO {table} "
                f"{self.__fields} "
                f"VALUES ({_str_query_complement}) "
                f"ON DUPLICATE KEY UPDATE {_str_query_values};")

            self.__cursor.executemany(_str_query, _values)
            self.__connection.commit()

            _result = True

        except Error as error:
            print(f'Database update failed: {format(error)}')
            self.__connection.rollback()
            _result = False

        self.__connection.close()
        self.__cursor.close()

        return _result


    def delete_data(self, table: str, data_df: pd.DataFrame, field_to_operate: str) -> bool:
        """
        Resume: Deletes the given data from the specified table database using
            as key the passed field.
        Description: Deletes all the data matching the dataframe given on the 
            specified field.
        Args:
            database (str): Database name to connecto to.
            table (str): Table name to fetch the data from.
            data_df (pandas.DataFrame): Data to be used for the deletion within
                the table.
            field_to_operate (str): Field to use in the query.
            
        Returns:
            bool: True if the table database number of rows matches the given 
                dataframe, False otherwise.
        """
        _table = table
        self.__cursor = self.__create_cursor()
        _data_df = data_df.copy()
        _field_to_operate = field_to_operate
        _values = str(list(_data_df[_field_to_operate])).\
            translate(str.maketrans({'[': '(', ']': ')'}))
        _str_query =\
            f'DELETE FROM {_table} WHERE {_field_to_operate} IN {_values}'

        try:
            self.__cursor.execute(_str_query)
            self.__connection.commit()

            _row_count: int = self.__cursor.rowcount
            self.__connection.close()
            self.__cursor.close()
            
            _result = _row_count == _data_df.shape[0]
        
        except Error as error:
            print(f"ERROR: {error}. Check for None values in the dataframe.")
            _result = False
            
        return _result

    
    def truncate_table(self, table: str) -> bool:
        """
        Resume: Truncates the given table.
        Description: Deletes all the data from a table.
        Args:
            table (str): Table name to truncate.
            
        Returns:
            bool: True if the rowcount is zero, False otherwise.
        """
        _table = table
        self.__cursor = self.__create_cursor()
        _str_query =\
            f'TRUNCATE {_table};'
        
        self.__cursor.execute(_str_query)
        self.__connection.commit()

        _row_count_final: bool = self.__cursor.rowcount == 0
        self.__connection.close()
        self.__cursor.close()
        

        return _row_count_final


    def execute_custom_query(self, query: str) -> any:
        """
        Resume: Excutes a custom SQL query.
        Description: Excutes the given SQL query in the database.
        Args:
            table (str): Table name to fetch the data from.
            
        Returns:
            any: 
                boolean - True if the affected number is greater than -1 on UPDATE
                    and DELETE operations, False otherwise.
                pd.DataFrame: if the operation is a SELECT, returns the fetched data.
        """
        self.__cursor = self.__create_cursor()

        _str_query = query
        self.__cursor.execute(_str_query)
        
        if _str_query.__contains__('SELECT'):
            _results = self.__cursor.fetchall()
            _result = pd.DataFrame(data = _results, columns = self.__cursor.column_names)
        else:
            self.__connection.commit()
            _result = self.__cursor.rowcount > -1

        self.__connection.close()
        self.__cursor.close()

        return _result

# End-of-file (EOF)
