from typing import Any
from .parsing_validator import ParsingValidator


def parse_dict(lst: list[str]) -> dict[str, str | int]:
    meta: dict[str, str | int] = {}

    for word in lst:
        tmp: list[str] = word.split('=')
        key: str = tmp[0].removeprefix('[').removesuffix(']')
        val: str | int = tmp[1].removesuffix(']')
        val = int(val) if val.isdigit() else val.removesuffix(']')
        meta.update({key: val})

    return meta


def parse_meta_data(
    line: str


) -> dict[str, tuple[int, int] | dict[str, str | int]]:
    words: list[str] = line.split()

    name: str = words[1]
    position: tuple[int, int] = (int(words[2]), int(words[3]))
    dict_meta = parse_dict(words[4:])

    return {
        "name": name,
        "position": position,
        "meta": dict_meta
    }


def parse_connection(words: list[str]) -> dict[str, str]:
    zones: list[str] = words[1].split("-")
    return {
        "1": zones[0],
        "2": zones[1]
    }


def parse_map(
    map: str
) -> Any:
    n_drones: int = 0
    start: dict[str, tuple[int, int] | dict[str, str | int]] = {}
    end: dict[str, tuple[int, int] | dict[str, str | int]] = {}
    hub: list[dict[str, tuple[int, int] | dict[str, str | int]]] = []
    connection: list[dict[str, str]] = []

    lines = map.split("\n")
    for line in lines:
        if line.startswith('#') or len(line.strip()) == 0:
            continue
        if line.startswith('start_hub'):
            start = parse_meta_data(line)
        elif line.startswith('end_hub'):
            end = parse_meta_data(line)
        elif line.startswith('hub'):
            hub.append(parse_meta_data(line))
        elif line.startswith('connection'):
            connection.append(parse_connection(line.split()))
        elif line.startswith("nb_drones"):
            n_drones = int(line.split()[1])

    return n_drones, start, end, hub, connection


def open_map(map_name: str) -> None:
    n_drones: int = 0
    start: dict[str, str | tuple[int, int] | dict[str, str | int]] = {}
    end: dict[str, str | tuple[int, int] | dict[str, str | int]] = {}
    hub: list[dict[str, str | tuple[int, int] | dict[str, str | int]]] = []
    connection: list[dict[str, str]] = []

    try:
        with open(map_name, "r") as f:
            n_drones, start, end, hub, connection = parse_map(f.read())

            ParsingValidator(
                n_drones=n_drones,
                start=start,
                end=end,
                hub=hub,
                connection=connection
            )
    except Exception as e:
        print(f"Error occurred while opening the map file: {e}")
