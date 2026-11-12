import argparse
import duckdb

from pathlib import Path


def check_input_path(
        path: Path, 
        filetype: str | None
) -> None:
    """
    Checking input path

    Args:
        path (Path): path to input file or directory
        filetype (str): extension of input file or None if input path is a directory

    Returns:
        None

    Raises:
        FileNotFoundError: if input path does not exist
        NotADirectoryError: if path is not a directory when needs a directory
        IsADirectoryError: if path is a directory when needs a file
        ValueError: if path has incorrect extension
    """
    if filetype is None:
        if path.exists():
            if not path.is_dir():
                raise NotADirectoryError(f"Path {path} is not a directory")
        else:
            raise FileNotFoundError(f"Path {path} does not exist")

    else:    
        if not path.exists():
            raise FileNotFoundError(f"Path {path} does not exist")

        if not path.is_file():
            raise IsADirectoryError(f"Path {path} is not a file")

        if filetype == ".sql":
            if path.suffix.lower() != ".sql":
                raise ValueError(
                    f"File {path} has incorrect extension: {path.suffix}"
                )        

            print(f"SQL path {path} is checked successfully")

        elif filetype == ".csv":
            if path.suffix.lower() != ".csv":
                raise ValueError(
                    f"File {path} has incorrect extension: {path.suffix}"
                )     

            print(f"CSV path {path} is checked successfully")

        else:
            raise ValueError(f"Incorrect filetype {filetype}")


def main() -> None:
    """
    Extract data from CSV and load to DuckDB
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "csv_path",
        type=Path,
        help="Path to the input CSV file"
    )

    args = parser.parse_args()
    csv_path = args.csv_path

    root_path = Path(__file__).resolve().parent.parent
    duckdb_path = root_path / "data" / "bank_transactions.duckdb"
    parquet_path = duckdb_path.with_name("bank_transactions.parquet")
    duckdb_parent_dir = duckdb_path.resolve().parent
    create_bank_transactions_table_path = root_path / "sql" / "create_bank_transactions.sql"
    truncate_bank_transactions_table_path = root_path / "sql" / "truncate_bank_transactions.sql"
    insert_into_bank_transactions_table_path = root_path / "sql" / "insert_into_bank_transactions.sql"
    count_bank_transactions_table_path = root_path / "sql" / "count_bank_transactions_table_rows.sql"

    check_input_path(
        path=duckdb_parent_dir,
        filetype=None
    )
    check_input_path(
        path=create_bank_transactions_table_path,
        filetype=".sql"
    )
    check_input_path(
        path=truncate_bank_transactions_table_path,
        filetype=".sql"
    )
    check_input_path(
        path=insert_into_bank_transactions_table_path,
        filetype=".sql"
    )
    check_input_path(
        path=count_bank_transactions_table_path,
        filetype=".sql"
    )
    check_input_path(
        path=csv_path,
        filetype=".csv"
    )

    create_bank_transactions_sql_query = create_bank_transactions_table_path.read_text(encoding="utf-8")
    truncate_bank_transactions_sql_query = truncate_bank_transactions_table_path.read_text(encoding="utf-8")
    insert_into_bank_transactions_sql_query = insert_into_bank_transactions_table_path.read_text(encoding="utf-8")
    count_bank_transactions_sql_query = count_bank_transactions_table_path.read_text(encoding="utf-8")

    with duckdb.connect(duckdb_path) as con:
        con.execute("INSTALL encodings; LOAD encodings")
        con.execute(create_bank_transactions_sql_query)
        con.execute(
            """
            BEGIN TRANSACTION
            """
        )

        try:
            con.execute(truncate_bank_transactions_sql_query)
            con.execute(
                insert_into_bank_transactions_sql_query,
                [str(csv_path)]
            )

            result = con.execute(count_bank_transactions_sql_query).fetchone()
            table_rows = result[0]
            if table_rows == 0:
                raise ValueError("Input CSV file is empty")

            con.execute("COMMIT")

        except Exception:
            con.execute("ROLLBACK")
            raise

        con.execute(f"COPY bank_transactions TO '{parquet_path}' (FORMAT parquet)")

        dataframe = con.execute(
            """
            SELECT *
            FROM bank_transactions
            LIMIT 5
            """
        ).df()

        print(dataframe)


if __name__ == "__main__":
    main()