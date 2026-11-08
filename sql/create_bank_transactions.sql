CREATE TABLE IF NOT EXISTS bank_transactions (
    operation_date DATE,
    processing_datetime TIMESTAMP,
    operation_code VARCHAR,
    operation_description VARCHAR,
    operation_amount DECIMAL(38, 2),
    balance_after_operation DECIMAL(38, 2)
)