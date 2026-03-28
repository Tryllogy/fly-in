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
        self.belonging: list[dict[str, list[str]]] = []
        self.start["meta"]["actual_drones"] = n_drones

        self.create_drones()
        self.make_belonging()

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
        for b in self.belonging:
            print(f"Belonging : {list(b.keys())[0]}: {list(b.values())[0]}")
        print()
        for d in self.drones:
            print(f"Drone {list(d.keys())[0]}: {list(d.values())[0]}")


    def create_drones(self) -> None:
        for i in range(1, self.n_drones + 1):
            self.drones.append({
                i: self.start["name"]
            })
            
    def make_belonging(self) -> None:
        names: set[str] = set()
        for con in self.connection:
            if con["1"] not in names:
                names.add(con["1"])
                self.belonging.append({con["1"]: []})
                
            if con["2"] not in names:
                names.add(con["2"])
                self.belonging.append({con["2"]: []})

            for belong in self.belonging:
                for key, v in belong.items():
                    if key == con["1"]:
                        belong[con["1"]].append(con["2"])
                        parent: Optional[str] = self.make_parents(con["1"])
                        if parent is not None and parent not in v:
                            belong[con["1"]].append(parent)
                    
                    if key == con["2"]:
                        belong[con["2"]].append(con["1"])
                        parent: Optional[str] = self.make_parents(con["2"])
                        if parent is not None and parent not in v:
                            belong[con["2"]].append(parent)
                            

    def make_parents(
        self, 
        name: str
    ) -> str:
        for b in self.belonging:
            for k, v in b.items():
                if name in v:
                    return k
        return None

    def move_drones(self) -> None:
        finished: int = 0
        while finished < self.n_drones:
            finished: int = 0
            
            for d in self.drones:
                id_drone, name_zone = next(iter(d.items()))
                if name_zone == self.end["name"]:
                    finished += 1
                    continue
            
                if self.step(d):
                    _, name_zone = next(iter(d.items()))
                    print(f"D{id_drone}-{name_zone}", end=" ")
            print()

    def step(
        self,
        drone
    ) -> bool:
        name: str = list(drone.values())[0]
        visited: dict[str, int] = {name: 0}
        path: list[str] = [name]
        length: int

        while len(path) >= 1:
            actual: str = path.pop()
            length = visited[actual]
            neighbors: list = self.get_neighbors(actual)

            if neighbors is None:
                raise ValueError("No neighbors found")

            for n in neighbors:
                if (n not in visited and not self.check_status(name, "blocked")):
                    visited.update({n: length + 1})
                    path.append(n)
                elif (n in visited and not self.check_status(name, "blocked")):
                    if length + 1 < visited[n]:
                        visited.update({n: length + 1})
                        path.append(n)

        return self.move_shortest(drone, visited)

    def move_shortest(
        self,
        drone,
        path
    ) -> bool:
        actual: tuple[str, int]
        
        for k, v in path.items():
            if k == self.end["name"]:
                actual = (k, v)
                break
        
        while actual[1] != 1:
            parents = self.get_parent(actual, path)
            n_parents: int = len(parents)
            if n_parents == 0:
                return False

            for p in parents:
                if self.check_status(p[0], "priority") and self.check_capacity(p[0]):
                    actual = p
                    break
                elif self.check_capacity(p[0]):
                    actual = p
                else:
                    actual = None

            if actual is None:
                return False

        self.update_pos(drone, actual)
        return True

    def update_pos(self, drone: dict, pos: tuple[str, int]) -> None:
        id_drone, pos_drone = next(iter(drone.items()))


        if pos_drone == self.start["name"]:
            self.start["meta"]["actual_drones"] -= 1
        if pos[0] == self.end["name"]:
            self.end["meta"]["actual_drones"] += 1

        for h in self.hub:
            if h["name"] == pos_drone:
                h["meta"]["actual_drones"] -= 1
            if h["name"] == pos[0]:
                h["meta"]["actual_drones"] += 1

        drone.update({id_drone: pos[0]})

    def get_parent(
        self,
        actual: tuple[str, int],
        path
    ) -> tuple[str, int]:
        possible_neighbors: list[tuple[str, int]] = []
        for k, v in path.items():
            if v == actual[1] - 1:
                if self.is_connected(k, actual):
                    possible_neighbors.append((k, v))

        return possible_neighbors

    def is_connected(
        self,
        name: str,
        actual: tuple[str, int]
    ) -> bool:
        for b in self.belonging:
            for k, v in b.items():
                if k == name:
                    if actual[0] in v:
                        return True

        return False
    
    def check_capacity(
        self,
        name: str
    ) -> bool:
        for h in self.hub:
            if h["name"] == name:
                return h["meta"]["actual_drones"] + 1 <= h["meta"]["max_drones"]

        return False

    def check_connection_capacity(
        self,
        name
    ) -> bool:
        pass

    def check_status(
        self,
        name: str,
        status: str
    ) -> bool:
        for h in self.hub:
            if h["name"] == name:
                for k, v in h["meta"].items():
                    if k == "zone" and v == status:
                        return True

        return False

    def get_neighbors(
        self,
        name
    ) -> list:
        for b in self.belonging:
            for k, v in b.items():
                if k == name:
                    return v
        
        return None
