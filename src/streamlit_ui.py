from io import BytesIO

import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from modules.compare_data import CompareData
from modules.database import Database

if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = False
if "file_processed" not in st.session_state:
    st.session_state["file_processed"] = False

def file_separator():
    separators = [",",";","|","§"]
    option = st.segmented_control(
        label="File separator",
        options=separators,
        selection_mode="single",
        default=separators[0],
    )
    return option

def upload_files() -> tuple[UploadedFile, UploadedFile, str]:
    st.header("Upload files")
    file1 = st.file_uploader(label="Upload file1", type=["csv"], accept_multiple_files=False, key="file1")
    file2 = st.file_uploader(label="Upload file2", type=["csv"], accept_multiple_files=False, key="file2")
    separator = file_separator()
    btn = st.button("Upload files")
    if btn:
        st.session_state["uploaded_file"] = True
    return file1, file2, separator


def process_files(file1: UploadedFile, file2: UploadedFile, sep: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    if st.session_state["uploaded_file"]:
        if sep is None:
            sep = ","
        if file1 is not None and file2 is not None:
            try:
                file1_df = pd.read_csv(file1, dtype=str, sep=sep)
                file2_df = pd.read_csv(file2, dtype=str, sep=sep)
                st.toast("Files Uploaded!!!")
                st.session_state["file_processed"] = True
                return file1_df, file2_df
            except Exception as e:
                st.error(e)
                return pd.DataFrame(), pd.DataFrame()
    return pd.DataFrame(), pd.DataFrame()


def setup_database(file1_df: pd.DataFrame, file2_df: pd.DataFrame) -> Database:
    db = Database(":memory:")
    db.insert_df_data("table1", file1_df)
    db.insert_df_data("table2", file2_df)
    return db


def validate_tables(db: Database) -> list[str]:
    tb1_cols = db.get_columns("table1")
    tb2_cols = db.get_columns("table2")
    if tb1_cols != tb2_cols:
        st.error("Tables must have the same columns")
        st.stop()
    st.success("Tables have the same columns")
    return tb1_cols


def user_inputs(tb1_cols: list[str]) -> tuple[list[str], str, int, str]:
    join_columns = st.multiselect("Columns to join", tb1_cols)
    compare_column = st.selectbox("Column to compare", tb1_cols)
    key_column = st.selectbox("Column to be a key", tb1_cols)

    if compare_column in join_columns:
        st.error("Compare column must not be in join columns")
        st.stop()

    if key_column in join_columns or key_column in compare_column:
        st.error("Compare column must not be in join columns or compare column")
        st.stop()

    filter_value = st.slider("Select filter", 0, 100, 80)
    return join_columns, compare_column, filter_value, key_column


def execute_comparison(db: Database, join_columns: list[str], compare_column: str, filter_value: int, key_column: str) -> None:
    with st.spinner("Comparing data..."):
        cd = CompareData(db)
        cd.compare(join_columns, compare_column)
        report_df = cd.report(join_columns, compare_column, key_column, filter_value)
        if report_df is not None:
            output = BytesIO()
            report_df.to_csv(output, index=False)
            output.seek(0)
            st.download_button(label="Download Report", data=output, file_name="comparison_report.csv", mime="text/csv")
            st.success("Comparison completed. Download available.")


def main() -> None:
    st.title("Web GUI - TextSim Analyzer")
    file1, file2, separator = upload_files()
    file1_df, file2_df = process_files(file1, file2, separator)
    if not file1_df.empty and not file2_df.empty and st.session_state["file_processed"]:
        db = setup_database(file1_df, file2_df)
        tb1_cols = validate_tables(db)
        join_columns, compare_column, filter_value, key_column = user_inputs(tb1_cols)

        check_key_1 = file1_df[key_column].isnull().any()
        check_key_2 = file2_df[key_column].isnull().any()

        if not check_key_1 or not check_key_2:
            st.error("The key columns must be filled")
            st.stop()

        if st.button("Execute"):
            execute_comparison(db, join_columns, compare_column, filter_value, key_column)


if __name__ == "__main__":
    main()
