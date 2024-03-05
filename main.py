import avito_parser
import argparse


def main():
    arg_parser = argparse.ArgumentParser(description="Avito parse CLI app")
    arg_parser.add_argument("url", type=str, help="URL to parse")
    arg_parser.add_argument("csv_path", type=str, help="Path to save CSV")
    arg_parser.add_argument("--count", type=int, default=15, help="How many products to parse")
    arg_parser.add_argument("--max_price", type=int, default=0, help="Max price")
    arg_parser.add_argument("--min_price", type=int, default=0, help="Min price")
    arg_parser.add_argument("--address", type=str, default="", help="Address")
    arg_parser.add_argument("--log_level", type=int, default=0, help="0 - success and errors, 1 - info, 2 - debug")
    arg_parser.add_argument("--keywords", type=str, default=[], help="Key words", nargs="+")
    arg_parser.add_argument("--version", action="version", version="Avito Parser 1.0")
    arg_parser.add_argument("--verbose", action="store_true", help="Verbose mode")  # TODO: Add verbose mode
    arg_parser.add_argument("--quiet", action="store_true", help="Quiet mode")  # TODO: Add quiet mode

    args = arg_parser.parse_args()

    parser = avito_parser.AvitoParse(
        url=args.url,
        csv_path=args.csv_path,
        keywords_list=args.keywords,
        count=args.count,
        max_price=args.max_price,
        min_price=args.min_price,
        address=args.address,
        log_level=args.log_level
    )

    for _ in parser.parse():
        pass


if __name__ == '__main__':
    main()
