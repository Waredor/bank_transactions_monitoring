from pathlib import Path
import argparse
import pymupdf


def extract_page_text(document: pymupdf.Document, page_number: int, page_count: int) -> str:
    """Extract text from PDF page"""
    if 0 <= page_number < page_count:
        page = document.load_page(page_number)
        page_text = page.get_text()
        print(f"Page: {page_number} extracted successfully")

    else:
        raise ValueError(f"Page number {page_number} is incorrect")

    return page_text


def write_text_file(page_text: str, page_number: int, output_txt_path: Path) -> None:
    """Write text to TXT file"""
    with open(output_txt_path, mode="w", encoding="utf-8") as output_document:
        output_document.write(page_text)
        print(f"Text from PDF page {page_number} was successfully written to TXT")


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
        page_count = document.page_count
        print(f"Number of pages: {page_count}")

        page_number = 0

        page_text = extract_page_text(document, page_number=page_number, page_count=page_count)

    write_text_file(page_text, page_number, output_txt_path)

if __name__ == "__main__":
    main()