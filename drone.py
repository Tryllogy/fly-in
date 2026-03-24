from typing import Any, Optional

class Drone:
    turn: int = 0
    
    def __init__(
        self,
        n_drones: int,
        start: dict[str, str | tuple[int, int] | dict[str, str | int]],
        end: dict[str, str | tuple[int, int] | dict[str, str | int]],
        hub: list[dict[str, str | tuple[int, int] | dict[str, str | int]]],
        connection: list[dict[str, str | int]]
    ) -> None:
        self.n_drones: int = n_drones
        self.drones: list[dict[int, dict[str, str | tuple[int, int]
                            | dict[str, str | int]]]] = []
        self.start: dict[str, str | tuple[int, int]
                         | dict[str, str | int]] = start
        self.end: dict[str, str | tuple[int, int] | dict[str, str | int]] = end
        self.hub: list[dict[str, str | tuple[int, int]
                            | dict[str, str | int]]] = hub
        self.connection: list[dict[str, str | int]] = connection
        self.n_hub: int = len(self.hub) + 2
        self.start["meta"]["actual_drones"] = n_drones

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
                i: self.start
            })

    def get_meta_from_str(self, name: str) -> Optional[Any]:
        if name == self.start["name"]:
            return self.start
        if name == self.end["name"]:
            return self.end
        for h in self.hub:
            if h["name"] == name:
                return h
        return None
    
    def get_neighbors(
        self,
        meta: Any
    ) -> list[tuple[int, int]]:
        neighbors: list[Any] = []
        
        for con in self.connection:
            if con["1"] == meta["name"]:
                meta_neighbor: Any = self.get_meta_from_str(con["2"])
                if (meta_neighbor["meta"].get("zone") is None
                    or meta_neighbor["meta"].get("zone") != "blocked"):
                    neighbors.append(meta_neighbor)
        return neighbors

    def move_drones(self) -> None:
        finished: int = 0
        while finished < self.n_drones:
            finished = 0
            for d in self.drones:

                id: int = list(d.keys())[0]
                meta: Any = list(d.values())[0]
                if meta["name"] == self.end["name"]:
                    finished += 1
                    continue
                
                meta_neighbors: list[Any] = self.get_neighbors(meta)
                if (self.step(d, meta_neighbors)):
                    meta = list(d.values())[0]
                    print(f"D{id}-{meta['name']}", end=" ")
            print()

            # TODO : Faire un vrai calcul pour le nombre de turn
            if finished < self.n_drones:
                Drone.turn += 1
        
        print(f"All drones finished, total turns: {Drone.turn}")

    def step(
        self,
        drone: Any,
        meta_neighbors: Any
    ) -> bool:
        # TODO : TROUVER LE MEILLEUR CHEMIN A PARTIR DE LA POSITION ACTUELLE
        # SI PAS DE PLACE SUR LE PROCHAIN HUB -> ATTENDRE
        # SI PRIORITY ALORS PASSER PAR LA SAUF SI PLEIN ET AUTRE CHEMIN

        # SI DRONE BOUGE ALORS RENVOYER true SINON false
        if len(meta_neighbors) < 1:
            raise ValueError("No neighbors")

        for n in meta_neighbors:
            if n["meta"].get("max_drones") and n["meta"]["actual_drones"] == n["meta"]["max_drones"]:
                continue
            
            n["meta"]["actual_drones"] += 1
            d_meta: Any = list(drone.values())[0]
            d_meta["meta"]["actual_drones"] -= 1
            drone.update({list(drone.keys())[0]: n})
            return True

        return False
