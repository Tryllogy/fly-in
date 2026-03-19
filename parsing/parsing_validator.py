from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from typing_extensions import Self


class ZoneEnum(Enum):
    NORMAL: int = 1
    BLOCKED: int = 2
    RESTRICTED: int = 3
    PRIORITY: int = 4


class ParsingValidator(BaseModel):
    n_drones: int = Field(...)
    start: dict[str, str | tuple[int, int] | dict[str, str | int]] = Field(...)
    end: dict[str, str | tuple[int, int] | dict[str, str | int]] = Field(...)
    hub: list[
        dict[str, str | tuple[int, int] | dict[str, str | int]]] = Field(...)
    connection: list[dict[str, str | int]] = Field(...)

    @classmethod
    def check_name(
        cls: "ParsingValidator",
        value: str
    ) -> None:
        if " " in value or "-" in value:
            raise ValueError(
                f"Zone name cannot contain spaces or dashes: {value}")

    @classmethod
    def meta(
        cls: "ParsingValidator",
        value: dict[str, str | int]
    ) -> None:
        for key, val in value["meta"].items():
            if not isinstance(key, str):
                raise ValueError(f"Meta keys must be strings: {key}")
            if not isinstance(val, (str, int)):
                raise ValueError(
                    f"Meta values must be strings or integers: {val}")
            if key == "color":
                if not isinstance(val, str):
                    raise ValueError(f"Color must be a string: {val}")
                words: list[str] = val.split(" ")
                if len(words) >= 2:
                    raise ValueError(f"Color must be a single string: {val}")
            if key == "max_drones":
                if val < 0:
                    raise ValueError(
                        f"Max drones must be a positive integer: {val}")
            if key == "zone":
                if val.upper() not in [zone.name for zone in ZoneEnum]:
                    raise ValueError(f"Invalid zone type: {val}")

    @field_validator("n_drones")
    @classmethod
    def validate_drones(
        cls: "ParsingValidator",
        value: int
    ) -> int:
        if (value <= 0):
            raise ValueError(
                f"Number of drones must be a positive integer: {value}")
        return value

    @field_validator("connection")
    @classmethod
    def validate_connection(
        cls: "ParsingValidator",
        value: list[str]
    ) -> list[str]:
        if not isinstance(value, list):
            raise ValueError(f"Connection must be a list of strings: {value}")
        for item in value:
            for key, val in item.items():
                if key == "max_link_capacity":
                    if not isinstance(val, int):
                        raise ValueError(
                            f"Max link capacity must be an integer: {val}")
                else:
                    if not isinstance(val, str):
                        raise ValueError(
                            f"Connection items must be strings: {val}")
        return value

    @model_validator(mode="after")
    def validate_meta_start_end(
        self
    ) -> Self:
        self.check_name(self.start["name"])
        self.check_name(self.end["name"])
        self.meta(self.start)
        self.meta(self.end)
        return self

    @model_validator(mode="after")
    def validate_meta_hub(
        self
    ) -> Self:
        for hub in self.hub:
            for h2 in self.hub:
                if hub != h2 and hub["name"] == h2["name"]:
                    raise ValueError(
                        f"Two hubs cannot have the same name: {hub['name']}")
            if (hub["name"] == self.start["name"]
                    or hub["name"] == self.end["name"]):
                raise ValueError(
                    "Hub name cannot be the same as start "
                    f"or end hub: {hub['name']}")
            self.check_name(hub["name"])
            self.meta(hub)
        return self

    @model_validator(mode="after")
    def validate_start_end_drones(
        self
    ) -> Self:
        if self.start['meta'].get("max_drones") is not None:
            if (self.start['meta']["max_drones"] != self.n_drones):
                raise ValueError(
                    "Start hub has incorrect number "
                    f"of drones: {self.n_drones}")

        if self.end['meta'].get("max_drones") is not None:
            if (self.end['meta']["max_drones"] != self.n_drones):
                raise ValueError(
                    f"End hub has incorrect number of drones: {self.n_drones}")
        return self

    @model_validator(mode="after")
    def validate_connection_names(
        self
    ) -> Self:
        names: list[str] = []
        for hub in self.hub:
            names.append(hub["name"])
        names.append(self.start["name"])
        names.append(self.end["name"])
        for connection in self.connection:
            if connection["1"] not in names or connection["2"] not in names:
                raise ValueError(
                    "Invalid connection: hub not found: "
                    f"\'{connection['1']}\' or \'{connection['2']}\'")
        return self

    @model_validator(mode="after")
    def validate_connection_unique_link(
        self
    ) -> Self:
        for i, connection in enumerate(self.connection):
            for j, other_connection in enumerate(self.connection):
                if i != j:
                    if ((connection["1"] == other_connection["1"]
                        and connection["2"] == other_connection["2"])
                        or (connection["1"] == other_connection["2"]
                            and connection["2"] == other_connection["1"])):
                        raise ValueError(
                            "Duplicate connection found: "
                            f"\'{connection['1']}\' -> \'{connection['2']}\'")

        return self
