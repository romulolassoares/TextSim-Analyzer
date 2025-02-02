from src.modules.database import Database
import jellyfish
from rapidfuzz import fuzz, utils

def calculate_jaro(a: str, b: str) -> float:
    result = jellyfish.jaro_winkler_similarity(a, b)
    result *= 100
    return float(f"{result:.2f}")

def calculate_wratio(a: str, b: str) -> float:
    result = fuzz.WRatio(a, b, processor=utils.default_process)
    return float(f"{result:.2f}")


class CompareData:
    def __init__(self, db: Database):
        self.db = db
        self.register_functions()
        pass

    def compare(self, join_columns:list, compare_col: str) -> None:
        tb1_cols = self.db.get_columns("table1")
        tb2_cols = self.db.get_columns("table2")

        all_elements_exists = all(element in tb1_cols for element in join_columns)
        if not all_elements_exists:
            raise Exception("Join columns are missing")

        if compare_col not in tb1_cols:
            raise Exception("Compare column are missing")

        join = ' and '.join([f"a.{col} = b.{col}" for col in join_columns])
        
        tb1_select = ", ".join([f"a.{col} as {col}_tb1" for col in tb1_cols])
        tb2_select = ", ".join([f"b.{col} as {col}_tb2" for col in tb2_cols])

        query = f"""
            create or replace table compare_table as
            select {tb1_select}, {tb2_select}, cast(0.0 as float) as jaro_winkler, cast(0.0 as float) as wratio
            from table1 a
            inner join table2 b
            on {join}
        """
        self.db.execute(query)

        query = f"""
            update compare_table set
            jaro_winkler = coalesce(calculate_jaro({compare_col}_tb1, {compare_col}_tb2),0),
            wratio = coalesce(calculate_wratio({compare_col}_tb1, {compare_col}_tb2),0)
        """
        self.db.execute(query)

        print("Completed")

    def report(self, join_columns: list, compare_col: str, filter :float = 0) -> None:
        all_columns = join_columns
        all_columns.append(compare_col)

        select = ", ".join(f"{col}_tb1, {col}_tb2" for col in all_columns)
        select = f"{select}, jaro_winkler, wratio"
        print(select)

        query = f"""
            select {select} from compare_table
            where jaro_winkler >= {filter}
            and wratio >= {filter}
        """

        df = self.db.execute(query).df()
        df.to_csv("compare_data.csv", index=False)

    def register_functions(self):
        self.db.register_function("calculate_jaro", calculate_jaro)
        self.db.register_function("calculate_wratio", calculate_wratio)