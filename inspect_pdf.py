from pathlib import Path
import argparse


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

    if not pdf_path.exists():
        parser.error(f"Path {pdf_path} does not exist")

    if not pdf_path.is_file():
        parser.error(f"Path {pdf_path} is not a file")

    if pdf_path.suffix.lower() != ".pdf":
        parser.error(f"File {pdf_path} has incorrect extension: {pdf_path.suffix}")

    print(f"PDF path {pdf_path} is checked successfully")


if __name__ == "__main__":
    main()