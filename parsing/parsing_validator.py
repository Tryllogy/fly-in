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
    connection: list[dict[str, str]] = Field(...)

    @classmethod
    def meta(cls, value: dict[str, str | int]):
        for key, val in value["meta"].items():
            if not isinstance(key, str):
                raise ValueError("Meta keys must be strings")
            if not isinstance(val, (str, int)):
                raise ValueError("Meta values must be strings or integers")
            if key == "max_drones":
                if val < 0:
                    raise ValueError("Max drones must be a positive integer")
            if key == "zone":
                if val.upper() not in [zone.name for zone in ZoneEnum]:
                    raise ValueError("Invalid zone type")
        return value

    @field_validator("n_drones")
    @classmethod
    def validate_drones(
        cls: "ParsingValidator",
        value: int
    ) -> int:
        if (value <= 0):
            raise ValueError("Number of drones must be a positive integer")
        return value

    @field_validator("start", "end")
    @classmethod
    def validate_meta_start_end(
        cls: "ParsingValidator",
        value: dict[str, str | int]
    ) -> dict[str, str | int]:
        return cls.meta(value)

    @field_validator("hub")
    @classmethod
    def validate_meta_hub(
        cls: "ParsingValidator",
        value: list[dict[str, str | int]]
    ) -> list[dict[str, str | int]]:
        for hub in value:
            cls.meta(hub)
        return value

    @model_validator(mode="after")
    def validate_start_drones(
        self
    ) -> Self:
        if self.start['meta'].get("max_drones") is not None:
            if (self.start['meta']["max_drones"] != self.n_drones):
                raise ValueError("Start hub has incorrect number of drones")
        return self

    @model_validator(mode="after")
    def validate_end_drones(
        self
    ) -> Self:
        if self.end['meta'].get("max_drones") is not None:
            if (self.end['meta']["max_drones"] != self.n_drones):
                raise ValueError("End hub has incorrect number of drones")
        return self

    @field_validator("connection")
    @classmethod
    def validate_connection(
        cls: "ParsingValidator",
        value: list[str]
    ) -> list[str]:
        if not isinstance(value, list):
            raise ValueError("Connection must be a list of strings")
        for item in value:
            for key, val in item.items():
                if not isinstance(val, str):
                    raise ValueError("Connection items must be strings")
        return value
