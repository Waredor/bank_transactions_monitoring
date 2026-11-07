import argparse
import pymupdf
import decimal
import pandas as pd

from pathlib import Path
from decimal import Decimal


def extract_page_text(document: pymupdf.Document, page_number: int, page_count: int, text_type="blocks") -> str:
    """
    Exctract text from PDF page

    Args:
        document (pymupdf.Document): input pymupdf document
        page_number (int): number of pdf page
        page_count (int): total number of pages in pdf document
        text_type (str): mode of .get_text() function 
    
    Returns:
        page_text (str): text of pdf page
    """
        
    if 0 <= page_number < page_count:
        page = document.load_page(page_number)
        page_text = page.get_text(text_type)
        print(f"Page: {page_number} extracted successfully")

    else:
        raise ValueError(f"Page number {page_number + 1} is incorrect")

    return page_text


def extract_all_operations(document: pymupdf.Document) -> list:
    """
    Extract text from all pages of input PDF document

    Args:
        document (pymupdf.Document): input pymupdf document 
    
    Returns:
        merged_pages (list): list of operations from input document
    """
    page_count = document.page_count
    print(f"Number of pages: {page_count}")

    merged_pages = []

    for page_number in range(page_count):
        page_text = extract_page_text(document=document, page_number=page_number, page_count=page_count)
        
        filtered_page_text = filter_content_blocks(page_text, page_number)
        grouped_page_text = group_blocks_by_row(filtered_page_text)
        filtered_grouped_page_text = filter_grouped_blocks(grouped_page_text)

        merged_grouped_page_text = []
        for group in filtered_grouped_page_text:
            merged_group = merge_operation_blocks(group)
            merged_grouped_page_text.append(merged_group)

        preprocessed_operations_list = create_operation_list(merged_grouped_page_text)
        merged_pages.extend(preprocessed_operations_list)

    return merged_pages


def write_text_file(full_text: str, output_txt_path: Path) -> None:
    """
    Write text to TXT file

    Args:
        full_text (str): full input text 
        output_txt_path (Path): path to output TXT file
    
    Returns:
        None
    """
    with open(output_txt_path, mode="w", encoding="utf-8") as output_document:
        output_document.write(full_text)
        print("Text from PDF file was successfully written to TXT")


def filter_content_blocks(blocks: list, page_number: int) -> list:
    """
    Filter content blocks

    Args:
        blocks (list): list of tuples with pdf info
        page_number (int): number of pdf page (starts from 0)
    
    Returns:
        filtered_blocks (list): list of filtered blocks with only operations content

    Raises:
        ValueError: if the marker text is not found in the page blocks
    """
    table_header_bottom = None

    marker_text = "ОСТАТОК СРЕДСТВ\n"
        
    for block in blocks:
        if block[4] == marker_text:
            table_header_bottom = block[3]
            break
        
    if table_header_bottom is not None:
        filtered_blocks = [block for block in blocks if block[1] > table_header_bottom]

    else:
        raise ValueError(f"Can't filter blocks on page {page_number + 1}")

    return filtered_blocks


def group_blocks_by_row(filtered_blocks: list, tolerance: float = 0.01) -> list:
    """
    Group PDF text blocks into table rows

    Args:
        filtered_blocks (list): list of filtered blocks
        tolerance (int): tolerance between y coordinates in one group
    
    Returns:
        grouped_blocks (list): list of grouped blocks
    """
    if len(filtered_blocks) == 0:
        return []

    sorted_blocks = sorted(filtered_blocks, key=lambda x: x[1])
    grouped_blocks = []
    current_group = []
    current_y = sorted_blocks[0][1]
    for block in sorted_blocks:
        if abs(block[1] - current_y) <= tolerance:
            current_group.append(block)
        else:
            grouped_blocks.append(current_group)
            current_y = block[1]
            current_group = []
            current_group.append(block)

    grouped_blocks.append(current_group)

    return grouped_blocks


def filter_grouped_blocks(
        grouped_blocks: list, expected_group_size: int = 2
) -> list:
    """
    Filter grouped content blocks

    Args:
        grouped_blocks (list): list of groups of tuples
        expected_group_size (int): expected number of elements in groups
    
    Returns:
        filtered_grouped_blocks (list): list of filtered groups of tuples
    """
    filtered_grouped_blocks = [
        block for block in grouped_blocks if len(block) == expected_group_size
    ]

    return filtered_grouped_blocks


def merge_operation_blocks(group: list) -> dict:
    """
    Merge blocks of one operation

    Args:
        group (list): a group of blocks
    
    Returns:
        merged_blocks (dict): A dict with merged information of one operation
    """
    if len(group) != 2:
        raise ValueError(
            f"Expected number of elements in group is 2, but group has {len(group)} elements"
        )
    
    if group[0][0] < group[1][0]:
        description_text = group[0][4]
        financial_data_text = group[1][4]

    else:
        description_text = group[1][4]
        financial_data_text = group[0][4]

    merged_blocks = {
        "description": description_text,
        "financial_data": financial_data_text
    }

    return merged_blocks


def parse_description(description: str) -> dict:
    """
    Parse description of financial operation

    Args:
        description (str): description of financial operation

    Returns:
        description_fields (dict): dict of operation fields

    Raises:
        ValueError: If the description contains fewer than five lines.  
    """
    filtered_description = description

    if description and description[-1] == "\n":
        filtered_description = description[:-1]
    
    description_elements = filtered_description.split("\n")
    if len(description_elements) < 5:
        raise ValueError(
            f"Not enough fields in description: expected at least 5 lines, but got {len(description_elements)}"
        )

    operation_date = description_elements[0]
    processing_datetime = " ".join(description_elements[1:3])
    operation_code = description_elements[3]
    operation_description = " ".join(description_elements[4:])

    description_fields = {
        "operation_date": operation_date,
        "processing_datetime": processing_datetime,
        "operation_code": operation_code,
        "operation_description": operation_description 
    }

    return description_fields


def parse_financial_data(financial_data: str) -> dict:
    """
    Parse financial data of financial operation

    Args:
        financial_data (str): financial_data for a financial operation

    Returns:
        financial_fields (dict): dict of financial data fields

    Raises:
        ValueError: If the number of fields in financial_data != 2.  
    """
    filtered_financial_data = financial_data

    if filtered_financial_data and filtered_financial_data[-1] == "\n":
        filtered_financial_data = filtered_financial_data[:-1]

    financial_data_elements = filtered_financial_data.split("\n")

    if len(financial_data_elements) != 2:
        raise ValueError(
            f"Invalid number of lines in financial_data: expected 2 lines, but got {len(financial_data_elements)}"
        )

    operation_amount = financial_data_elements[0]
    balance_after_operation = financial_data_elements[1]

    financial_fields = {
        "operation_amount": operation_amount,
        "balance_after_operation": balance_after_operation
    }

    return financial_fields


def normalize_amount(amount: str, is_operation: bool = False) -> Decimal:
    """
    Normalize an amount value and convert it to Decimal

    Args:
        amount (str): amount of financial operation
        is_operation (bool): type of amount 
            (operation amount when is_operation is True or balance after operation when is_operation is False)

    Returns:
        final_decimal_amount (Decimal): normalized amount

    Raises:
        ValueError: when input amount has incorrect format/ amount is not finite
            or amount couldn't be converted to Decimal
    """
    if not amount or amount.isspace():
        raise ValueError("Incorrect format of input amount")

    preprocessed_amount = amount.replace("\xa0", "").replace(",", ".")

    contains_whitespace = any(char.isspace() for char in preprocessed_amount)

    if (not preprocessed_amount) or (contains_whitespace):
        raise ValueError("Incorrect format of input amount")

    try:
        decimal_amount = Decimal(preprocessed_amount)
    except decimal.InvalidOperation as e:
        raise ValueError(
            f"Couldn't convert amount {preprocessed_amount} to decimal due to exception:"
        ) from e

    if not decimal_amount.is_finite():
        raise ValueError("Amount is not finite")

    if is_operation:
        if preprocessed_amount[0] == "-":
            raise ValueError("Incorrect format of input amount")

        if decimal_amount == Decimal("0"):
            final_decimal_amount = Decimal("0")

        elif preprocessed_amount[0] != "+":
            final_decimal_amount = -decimal_amount

        else:
            final_decimal_amount = decimal_amount

    else:
        if preprocessed_amount[0] == "-" or preprocessed_amount[0] == "+":
            raise ValueError("Incorrect format of input amount")
        
        if decimal_amount == Decimal("0"):
            final_decimal_amount = Decimal("0")

        else:
            final_decimal_amount = decimal_amount

    return final_decimal_amount


def create_single_operation(merged_operation: dict) -> dict:
    """
    Create dict with info of single operation
    
    Args:
        merged_operation (dict): input dict from function merge_operation_blocks() with description and financial data of operation
    
    Returns:
        operation (dict): parsed operation info
    """
    parsed_description = parse_description(merged_operation["description"])
    parsed_financial_data = parse_financial_data(merged_operation["financial_data"])

    normalized_operation_amount = normalize_amount(parsed_financial_data["operation_amount"], is_operation=True)
    normalized_balance_after_operation = normalize_amount(parsed_financial_data["balance_after_operation"], is_operation=False)

    operation = {
        "operation_date": parsed_description["operation_date"],
        "processing_datetime": parsed_description["processing_datetime"],
        "operation_code": parsed_description["operation_code"],
        "operation_description": parsed_description["operation_description"],
        "operation_amount": normalized_operation_amount,
        "balance_after_operation": normalized_balance_after_operation
    }

    return operation


def create_operation_list(grouped_list: list) -> list:
    """
    Create list of structured operations

    Args:
        grouped_list (list): input list of grouped data

    Return:
        operation_list (list): output list of structured operations
    """
    operation_list = []
    for group in grouped_list:
        single_operation_dict = create_single_operation(group)
        operation_list.append(single_operation_dict)

    return operation_list


def create_operations_dataframe(all_operations_list: list) -> pd.DataFrame:
    """
    Create pandas dataframe with all operations

    Args:
        all_operations_list (list): list of preprocessed operations

    Returns:
        output_df (pd.DataFrame): pandas dataframe with operations

    """
    columns = [
        "operation_date",
        "processing_datetime",
        "operation_code",
        "operation_description",
        "operation_amount",
        "balance_after_operation"
    ]
    if not all_operations_list:
        output_df = pd.DataFrame(columns=columns)

    else:
        output_df = pd.DataFrame(all_operations_list, columns=columns)

    return output_df


def main() -> None:
    """
    ETL function, which get input PDF path from CLI and export preprocessed dataframe to CSV
    Args:
        None
    Returns:
        None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the input PDF file"
    )

    args = parser.parse_args()
    pdf_path = args.pdf_path

    if not pdf_path.exists():
        parser.error(f"Path {pdf_path} does not exist")

    if not pdf_path.is_file():
        parser.error(f"Path {pdf_path} is not a file")

    if pdf_path.suffix.lower() != ".pdf":
        parser.error(f"File {pdf_path} has incorrect extension: {pdf_path.suffix}")        

    print(f"PDF path {pdf_path} is checked successfully")

    with pymupdf.open(pdf_path) as document:
        full_list_of_operations = extract_all_operations(document)

    operations_df = create_operations_dataframe(full_list_of_operations)
    output_csv_path = pdf_path.with_suffix(".csv")
    operations_df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")

    print(f"Output CSV path {output_csv_path} is created successfully")


if __name__ == "__main__":
    main()