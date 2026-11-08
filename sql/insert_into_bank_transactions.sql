INSERT INTO bank_transactions SELECT
    operation_date,
    processing_datetime,
    operation_code,
    operation_description,
    operation_amount,
    balance_after_operation
FROM read_csv(
    ?,
    delim=',',
    encoding='utf-8',
    dateformat='%d.%m.%Y',
    timestampformat='%d.%m.%Y %H:%M',
    columns={
        'operation_date': 'DATE',
        'processing_datetime': 'TIMESTAMP',
        'operation_code': 'VARCHAR',
        'operation_description': 'VARCHAR',
        'operation_amount': 'DECIMAL(38, 2)',
        'balance_after_operation': 'DECIMAL(38, 2)'
    }
);