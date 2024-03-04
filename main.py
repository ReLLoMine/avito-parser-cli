import avito_parser
import argparse


def main():
    arg_parser = argparse.ArgumentParser(description="Avito parse CLI app")
    arg_parser.add_argument("url", type=str, help="URL to parse")
    arg_parser.add_argument("csv_path", type=str, help="CSV file")
    arg_parser.add_argument("--count", type=int, default=15, help="How many pages to view")
    arg_parser.add_argument("--max_price", type=int, default=0, help="Max price")
    arg_parser.add_argument("--min_price", type=int, default=0, help="Min price")
    arg_parser.add_argument("--address", type=str, default="", help="Address")
    arg_parser.add_argument("--log_level", type=int, default=0, help="How many messages to show")
    arg_parser.add_argument("--keywords", type=str, default=[], help="Key words", nargs="+")

    args = arg_parser.parse_args()

    parser = avito_parser.AvitoParse(
        url=args.url,
        csv_path=args.csv_path,
        keysword_list=args.keywords,
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
