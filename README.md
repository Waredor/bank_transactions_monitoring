# Bank Transactions Monitoring

## Project Overview

**Bank Transactions Monitoring** is a personal data analytics project designed to process and analyze personal bank transactions.

The project currently implements an ETL pipeline that extracts transactions from a Sberbank PDF statement, converts them into a structured CSV file, and loads the data into a DuckDB database.

The long-term goal is to build an analytical solution for monitoring income and expenses, including transaction categorization and interactive dashboards.

## Implemented Features

### 1. Sberbank Statement Parser

- Extracts transaction data from a Sberbank PDF bank statement.
- Supports a specific Sberbank statement format.
- Processes all transactions included in the statement for the period selected by the user in the Sberbank application.
- Converts extracted data into a structured CSV file.

### 2. DuckDB Data Loader

- Loads transaction data from CSV into DuckDB.
- Uses SQL scripts for table creation, data truncation, and insertion.
- Implements a full refresh loading strategy.
- Uses database transactions to ensure atomicity.
- Validates the number of loaded records before committing changes.
- Rolls back the transaction if an error occurs, preserving the previously loaded data.

## Data Flow

```text
Sberbank PDF Statement
        |
        v
Bank Statement Parser
        |
        v
       CSV
        |
        v
DuckDB Data Loader
        |
        v
      DuckDB
        |
        v
Power BI Dashboard (Planned)
```

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | ETL development |
| PyMuPDF | PDF text extraction |
| Pandas | Data processing and CSV generation |
| DuckDB | Analytical database |
| SQL | Database operations and data loading |
| Power BI | Dashboard development (planned) |
| Git | Version control |

## Project Structure

```text
bank_transactions_monitoring/
├── data/
│   └── bank_transactions.duckdb
├── sql/
│   ├── create_bank_transactions.sql
│   ├── truncate_bank_transactions.sql
│   ├── insert_into_bank_transactions.sql
│   └── count_bank_transactions_table_rows.sql
├── src/
│   ├── parse_bank_statement.py
│   └── load_to_duckdb.py
├── tests/
├── .gitignore
└── README.md
```

## Data Schema

The `bank_transactions` table contains the following fields:

| Column | Data Type | Description |
|---|---|---|
| `operation_date` | DATE | Transaction date |
| `processing_datetime` | TIMESTAMP | Transaction processing date and time |
| `operation_code` | VARCHAR | Bank operation code |
| `operation_description` | VARCHAR | Transaction description |
| `operation_amount` | DECIMAL(38, 2) | Transaction amount |
| `balance_after_operation` | DECIMAL(38, 2) | Account balance after the transaction |

## Loading Strategy

The current implementation uses a **full refresh** approach.

Each loading run performs the following steps:

1. Starts a database transaction.
2. Truncates the existing `bank_transactions` table.
3. Loads transactions from the input CSV file.
4. Checks the number of records in the target table.
5. Commits the transaction if the table contains records.
6. Rolls back the transaction if an error occurs or the input dataset is empty.

This approach ensures that previously loaded data is preserved if the new dataset cannot be loaded successfully.

## Roadmap

- [ ] Develop a Power BI dashboard for income and expense analysis.
- [ ] Implement transaction categorization based on operation descriptions.
- [ ] Add automated ETL tests using `pytest`.
- [ ] Develop analytical data models and extend the project's analytical capabilities.
- [ ] Improve the data loading pipeline and consider incremental loading.

## Current Limitations

- The parser currently supports only one specific Sberbank PDF statement format.
- The statement period must be selected manually by the user.
- Transaction categorization has not yet been implemented.
- The data loader uses full refresh rather than incremental loading.
- Automated ETL tests have not yet been implemented.
- Power BI dashboard development is planned.

## Project Status

**Initial ETL pipeline implemented.**

The project currently supports extracting transactions from a Sberbank PDF statement, generating a structured CSV file, and loading the resulting data into DuckDB.