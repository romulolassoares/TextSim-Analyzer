import duckdb
import pandas as pd


class Database:
    def __init__(self, database: str) -> None:
        self.con = duckdb.connect(database=database, read_only=False)

    def insert_csv_data(self, name: str, file: str) -> None:
        self.con.execute(f"""
        CREATE OR REPLACE TABLE {name} AS
        SELECT * FROM read_csv('{file}', header = true, all_varchar = true);
        """)

    def insert_df_data(self, name: str, df: pd.DataFrame) -> None:
        self.con.execute(f"""
        CREATE OR REPLACE TABLE {name} AS
        SELECT * FROM df;
        """)


    def search_function(self, name: str) -> bool:
        function_check = f"""
        SELECT DISTINCT function_name
        FROM duckdb_functions()
        WHERE lower(function_type) = 'scalar'
        and function_name = '{name}' ORDER BY function_name;
        """
        res = self.con.execute(function_check).df()
        return res.empty

    def check_if_table_exists(self, table: str) -> bool:
        df = self.con.execute(f"SELECT * FROM duckdb_tables() WHERE TABLE_NAME = '{table}';").df()
        return df.empty

    def register_function(self, func_name: str, func_impl: callable) -> None:
        if not self.search_function(func_name):
            self.con.remove_function(func_name)
        self.con.create_function(func_name, func_impl)

    def execute(self, query: str):
        return self.con.execute(query)

    def get_columns(self, table_name: str) -> list:
        query = f"DESCRIBE {table_name}"
        return [row[0] for row in self.con.execute(query).fetchall()]