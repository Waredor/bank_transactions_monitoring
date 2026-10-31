from pathlib import Path
import argparse
import pymupdf


def extract_page_text(document: pymupdf.Document, page_number: int, page_count: int, text_type: str ="text") -> str:
    """Extract text from PDF page"""
    if 0 <= page_number < page_count:
        page = document.load_page(page_number)
        page_text = page.get_text("blocks")
        print(f"Page: {page_number} extracted successfully")

    else:
        raise ValueError(f"Page number {page_number + 1} is incorrect")

    return page_text


def extract_all_pages_text(document: pymupdf.Document) -> str:
    page_count = document.page_count
    print(f"Number of pages: {page_count}")

    page_texts = []

    for page_number in range(page_count):
        separator = f"--- PAGE {page_number + 1} ---"
        page_text = extract_page_text(document=document, page_number=page_number, page_count=page_count)
        page_texts.append(
            f"{separator}\n{page_text}"
        )

    full_text = "\n".join(page_texts)
    return full_text


def write_text_file(full_text: str, output_txt_path: Path) -> None:
    """Write text to TXT file"""
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
    if page_number >= 1:
        marker_text = "ОСТАТОК СРЕДСТВ\n"

    else:
        marker_text = "Расшифровка операций\n"
        
    for block in blocks:
        if block[4] == marker_text:
            table_header_bottom = block[3]
            break
        
    if table_header_bottom is not None:
        filtered_blocks = [block for block in blocks if block[1] > table_header_bottom]

    else:
        raise ValueError(f"Can't filter blocks on page {page_number + 1}")

    return filtered_blocks

def main() -> None:
    """The main function of this script"""
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