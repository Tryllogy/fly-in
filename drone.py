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
        self.drones: list[dict[int, tuple[int, int]]] = []
        self.start: dict[str, str | tuple[int, int]
                         | dict[str, str | int]] = start
        self.end: dict[str, str | tuple[int, int] | dict[str, str | int]] = end
        self.hub: list[dict[str, str | tuple[int, int]
                            | dict[str, str | int]]] = hub
        self.connection: list[dict[str, str | int]] = connection
        self.n_hub: int = len(self.hub) + 2

        self.create_drones()

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
        print()
        for d in self.drones:
            print(f"Drone {list(d.keys())[0]}: {list(d.values())[0]}")

    def get_positions(
        self
    ) -> list[tuple[int, int]]:
        positions: list[tuple[int, int]] = []
        positions.append(self.start["position"])
        positions.append(self.end["position"])
        for hub in self.hub:
            for pos in hub:
                if isinstance(hub[pos], tuple):
                    positions.append(hub[pos])
        return positions

    def set_map_dimension(self) -> None:
        self.map_min_width: int = min(
            min(list([hub[pos][1] for pos in hub
                      if isinstance(hub[pos], tuple)]
                     for hub in self.hub)),
            [self.end["position"][1]],
            [self.start["position"][1]]
        )[0]

        self.map_min_height: int = min(
            min(list([hub[pos][0] for pos in hub
                      if isinstance(hub[pos], tuple)]
                     for hub in self.hub)),
            [self.end["position"][0]],
            [self.start["position"][0]]
        )[0]

        self.map_max_width: int = max(
            max(list([hub[pos][1] for pos in hub
                      if isinstance(hub[pos], tuple)]
                     for hub in self.hub)),
            [self.end["position"][1]],
            [self.start["position"][1]]
        )[0]

        self.map_max_height: int = max(
            max(list([hub[pos][0] for pos in hub
                      if isinstance(hub[pos], tuple)]
                     for hub in self.hub)),
            [self.end["position"][0]],
            [self.start["position"][0]]
        )[0]

        self.map_width: int = abs(self.map_min_width) + abs(self.map_max_width)
        self.map_height: int = abs(
            self.map_min_height) + abs(self.map_max_height)

    def create_drones(self) -> None:
        for i in range(1, self.n_drones + 1):
            self.drones.append({
                i: self.start["position"]
            })

    def get_zone(
        self,
        pos: tuple[int, int]
    ) -> str:
        if pos == self.start["position"]:
            return self.start["name"]
        if pos == self.end["position"]:
            return self.end["name"]

        for h in self.hub:
            if h["position"] == pos:
                return h["name"]

        return "NONE"

    def move_drones(self) -> None:
        # TODO : BOUCLER JUSQUA CE QUE TOUS LES DRONES SOIENT SUR END
        for i in range(5):
            for d in self.drones:

                if list(d.values())[0] == self.end["position"]:
                    continue

                if (self.step(d)):
                    print(f"D{list(d.keys())[0]}-"
                          f"{self.get_zone(list(d.values())[0])}", end=" ")
            print()

    def step(
        self,
        drone: dict[int, tuple[int, int]]
    ) -> bool:
        # TODO : TROUVER LE MEILLEUR CHEMIN A PARTIR DE LA POSITION ACTUELLE
        # SI PAS DE PLACE SUR LE PROCHAIN HUB -> ATTENDRE
        # SI PRIORITY ALORS PASSER PAR LA SAUF SI PLEIN ET AUTRE CHEMIN
        # EVITER LES ZONES RESTRICTED

        # SI DRONE BOUGE ALORS RENVOYER true SINON false
        return True
