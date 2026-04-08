from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from typing import Any
from typing_extensions import Self


class ZoneEnum(Enum):
    """Enumeration of supported zone types."""

    NORMAL = 1
    BLOCKED = 2
    RESTRICTED = 3
    PRIORITY = 4


class ParsingValidator(BaseModel):
    """Validate the parsed map structure and business rules."""

    n_drones: int = Field(lt=2147483647)
    start: dict[str, Any] = Field(...)
    end: dict[str, Any] = Field(...)
    hub: list[dict[str, Any]] = Field(...)
    connection: list[dict[str, str | int]] = Field(...)

    @staticmethod
    def check_name(
        value: str
    ) -> None:
        """Validate that a zone name has no spaces or dashes.

        Args:
            value: Zone name to validate.

        Raises:
            ValueError: If the name contains unsupported characters.
        """
        if " " in value or "-" in value:
            raise ValueError(
                f"Zone name cannot contain spaces or dashes: {value}")

    @staticmethod
    def meta(
        value: dict[str, Any]
    ) -> None:
        """Validate metadata keys and values for a zone.

        Args:
            value: Zone dictionary containing a `meta` section.

        Raises:
            ValueError: If metadata schema or values are invalid.
        """
        meta_dict: Any = value.get("meta", {})
        for key, val in meta_dict.items():
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
                if (isinstance(val, int) and val <= 0) or \
                     (isinstance(val, str) and not val.isdigit()):
                    raise ValueError(
                        f"Max drones must be a positive integer: {val}")
            if key == "zone":
                if (isinstance(val, str) and val.upper() not
                        in [zone.name for zone in ZoneEnum]):
                    raise ValueError(f"Invalid zone type: {val}")

    @field_validator("n_drones")
    @classmethod
    def validate_drones(
        cls: type["ParsingValidator"],
        value: int
    ) -> int:
        """Validate that the drone count is strictly positive.

        Args:
            cls: Validator class reference.
            value: Declared drone count.

        Returns:
            The validated drone count.

        Raises:
            ValueError: If drone count is not positive.
        """
        if (value <= 0):
            raise ValueError(
                f"Number of drones must be a positive integer: {value}")
        return value

    @field_validator("connection")
    @classmethod
    def validate_connection(
        cls: type["ParsingValidator"],
        value: list[dict[str, str | int]]
    ) -> list[dict[str, str | int]]:
        """Validate connection field structure and capacity values.

        Args:
            cls: Validator class reference.
            value: Connection dictionaries to validate.

        Returns:
            The validated list of connections.

        Raises:
            ValueError: If connection entries are malformed.
        """
        if not isinstance(value, list):
            raise ValueError(f"Connection must be a list of dicts: {value}")
        for item in value:
            for key, val in item.items():
                if key == "max_link_capacity":
                    if not isinstance(val, int):
                        raise ValueError(
                            f"Max link capacity must be an integer: {val}")
                    elif val <= 0:
                        raise ValueError(
                            f"Max link capacity must be a "
                            f"positive integer: {val}")
                elif key != "connection_turn":
                    if not isinstance(val, str):
                        raise ValueError(
                            f"Connection items must be strings: {val}")
        return value

    @model_validator(mode="after")
    def validate_meta_start_end(
        self
    ) -> Self:
        """Validate names and metadata of start and end hubs.

        Returns:
            The validated model instance.
        """
        self.check_name(self.start["name"])
        self.check_name(self.end["name"])
        self.meta(self.start)
        self.meta(self.end)
        return self

    @model_validator(mode="after")
    def validate_meta_hub(
        self
    ) -> Self:
        """Validate intermediate hub uniqueness and metadata.

        Returns:
            The validated model instance.

        Raises:
            ValueError: If hub names conflict or metadata is invalid.
        """
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
        """Validate start and end capacities against drone count.

        Returns:
            The validated model instance.

        Raises:
            ValueError: If max capacities do not match `n_drones`.
        """
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
        """Validate that each connection references known zones.

        Returns:
            The validated model instance.

        Raises:
            ValueError: If a connection references unknown names.
        """
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
        """Ensure no duplicate or symmetric duplicate connection exists.

        Returns:
            The validated model instance.

        Raises:
            ValueError: If a duplicate link is found.
        """
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
