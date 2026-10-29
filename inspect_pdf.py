from pathlib import Path
import argparse


def main() -> None:
    """The main function of this script"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pdf_path",
        type=Path
    )
    parser.add_argument(
        "output_txt_path",
        type=Path
    )
    args = parser.parse_args()

    print(args.pdf_path, args.output_txt_path)


if __name__ == "__main__":
    main()