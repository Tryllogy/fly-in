class Drone:
    def __init__(
        self,
        n_drones: int,
        start: dict[str, str | tuple[int, int] | dict[str, str | int]],
        end: dict[str, str | tuple[int, int] | dict[str, str | int]],
        hub: list[dict[str, str | tuple[int, int] | dict[str, str | int]]],
        connection: list[dict[str, str | int]]
    ) -> None:
        self.n_drones: int = n_drones
        self.start: dict[str, str | tuple[int, int]
                         | dict[str, str | int]] = start
        self.end: dict[str, str | tuple[int, int] | dict[str, str | int]] = end
        self.hub: list[dict[str, str | tuple[int, int]
                            | dict[str, str | int]]] = hub
        self.connection: list[dict[str, str | int]] = connection

    @classmethod
    def from_file(cls, file_path: str) -> "Drone":
        from parsing.parsing import open_map
        n_drones, start, end, hub, connection = open_map(file_path)
        return cls(n_drones, start, end, hub, connection)

    def show_data(self) -> None:
        print(f"Number of drones: {self.n_drones}", end="\n\n")
        print(f"Start: {self.start}", end="\n\n")
        print(f"End: {self.end}", end="\n\n")
        for hub in self.hub:
            print(f"Hub: {hub}", end="\n")
        print()
        for con in self.connection:
            print(f"Connection: {con}", end="\n")
        print()
        print(f"Map width: {self.map_width}")
        print(f"Map height: {self.map_height}")

    def set_map(self) -> None:
        self.map_width: int = max(
            list([hub[pos][1] for pos in hub if isinstance(
                hub[pos], tuple)]for hub in self.hub),
            [[self.end["position"][1]]])[0]
        self.map_height: int = max(
            list([hub[pos][0] for pos in hub if isinstance(hub[pos], tuple)]
                 for hub in self.hub),
            [[self.end["position"][0]]]
        )[0]
