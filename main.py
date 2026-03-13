from parsing.parsing import open_map
import sys


def main() -> None:
    if len(sys.argv) == 1:
        print("Usage: python main.py <map_file>")
        return

    open_map(sys.argv[1])


if __name__ == "__main__":
    main()
