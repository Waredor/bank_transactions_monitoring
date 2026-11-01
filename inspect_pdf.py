from pathlib import Path
import argparse
import pymupdf


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


def extract_all_pages_text(document: pymupdf.Document) -> str:
    """
    Exctract text from all pages of input PDF document
    Args:
        document (pymupdf.Document): input pymupdf document 
    
    Returns:
        full_text (str): full text from input document
    """
    page_count = document.page_count
    print(f"Number of pages: {page_count}")

    page_texts = []

    for page_number in range(page_count):
        separator = f"--- PAGE {page_number + 1} ---"
        page_text = extract_page_text(document=document, page_number=page_number, page_count=page_count)
        
        filtered_page_text = filter_content_blocks(page_text, page_number)
        grouped_page_text = group_blocks_by_row(filtered_page_text)
        filtered_grouped_page_text = filter_grouped_blocks(grouped_page_text)

        page_texts.append(
            f"{separator}\n{filtered_grouped_page_text}"
        )

    full_text = "\n".join(page_texts)
    return full_text


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


def main() -> None:
    """
    ETL function of this script
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
    parser.add_argument(
        "output_txt_path",
        type=Path,
        help="Path to the output TXT file"
    )

    args = parser.parse_args()
    pdf_path = args.pdf_path
    output_txt_path = args.output_txt_path

    if not pdf_path.exists():
        parser.error(f"Path {pdf_path} does not exist")

    if not pdf_path.is_file():
        parser.error(f"Path {pdf_path} is not a file")

    if pdf_path.suffix.lower() != ".pdf":
        parser.error(f"File {pdf_path} has incorrect extension: {pdf_path.suffix}")

    if not output_txt_path.parent.exists():
        parser.error(
            f"Path to parent directory {output_txt_path.parent} does not exist"
        )

    if output_txt_path.suffix.lower() != ".txt":
        parser.error(
            f"File {output_txt_path} has incorrect extension: {output_txt_path.suffix}"
        )

    if output_txt_path.exists() and not output_txt_path.is_file():
        parser.error(
            f"{output_txt_path} is not path to file"
        )          

    print(f"PDF path {pdf_path} is checked successfully")
    print(f"TXT path {output_txt_path} is checked successfully")

    with pymupdf.open(pdf_path) as document:
        full_text = extract_all_pages_text(document)

    write_text_file(full_text, output_txt_path)

if __name__ == "__main__":
    main()