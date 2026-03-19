from typing import Any
from .parsing_validator import ParsingValidator


def parse_dict(lst: list[str]) -> dict[str, str | int]:
    meta: dict[str, str | int] = {}

    for word in lst:
        tmp: list[str] = word.split('=')
        if len(tmp) < 2:
            raise ValueError(f"Invalid meta format: {word}")
        key: str = tmp[0].removeprefix('[').strip()
        val: str | int = tmp[1].removesuffix(']').strip()
        val = int(val) if val.isdigit() else val
        if not (key == "zone" or key == "max_drones" or key == "color"):
            raise ValueError(f"Invalid meta key: {key}")
        meta.update({key: val})

    meta.update({"actual_drones": 0})
    return meta


def parse_meta_data(
    line: str
) -> dict[str, tuple[int, int] | dict[str, str | int]]:
    words: list[str] = line.split()

    name: str = words[1].strip()
    position: tuple[int, int] = (int(words[2].strip()), int(words[3].strip()))
    dict_meta = parse_dict(words[4:])

    return {
        "name": name,
        "position": position,
        "meta": dict_meta
    }


def parse_connection(words: list[str]) -> dict[str, str]:
    zones: list[str] = words[1].split("-")

    if len(words) == 3:
        max_link_capacity_words: list[str] = words[2].split("=")
        if (max_link_capacity_words[0].removeprefix("[").strip() ==
                "max_link_capacity"):
            max_link_capacity: int = int(
                max_link_capacity_words[1].removesuffix("]").strip())
        else:
            raise ValueError(
                f"Invalid connection meta key: {max_link_capacity_words[0]}")
    else:
        max_link_capacity: int = 1
    return {
        "1": zones[0],
        "2": zones[1],
        "max_link_capacity": max_link_capacity
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
    start_count: int = 0
    end_count: int = 0

    for line in lines:
        if line.strip().startswith('start_hub'):
            start_count += 1
        elif line.strip().startswith('end_hub'):
            end_count += 1
        if start_count >= 2 or end_count >= 2:
            raise ValueError("Only one start_hub and one end_hub allowed")

    if start_count == 0 or end_count == 0:
        raise ValueError("There must be exactly one start_hub and one end_hub")

    for i, line in enumerate(lines):
        try:
            if line.strip().startswith('#') or len(line.strip()) == 0:
                continue
            if line.strip().startswith('start_hub'):
                start = parse_meta_data(line)
            elif line.strip().startswith('end_hub'):
                end = parse_meta_data(line)
            elif line.strip().startswith('hub'):
                hub.append(parse_meta_data(line))
            elif line.strip().startswith('connection'):
                connection.append(parse_connection(line.split()))
            elif line.strip().startswith("nb_drones"):
                n_drones = int(line.split()[1])
        except Exception as e:
            raise ValueError(f"Error occurred while parsing line {i + 1}: {e}")

    return n_drones, start, end, hub, connection


def open_map(map_name: str) -> tuple[int, dict, dict, list, list]:
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

            for h in hub:
                if h["meta"].get("max_drones") is None:
                    h["meta"].update({"max_drones": 1})
                if h["meta"].get("color") is None:
                    h["meta"].update({"color": None})
                if h["meta"].get("zone") is None:
                    h["meta"].update({"zone": "normal"})

            return n_drones, start, end, hub, connection
    except Exception as e:
        print(f"Error occurred while opening the map file: {e}")
