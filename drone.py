from typing import Any, Optional, Generator
from copy import deepcopy

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

    def move_drones(self) -> Generator:
        turn: int = 0
        print()
        while self.end["meta"]["actual_drones"] != self.n_drones:
            moved: int = 0
            for d in self.drones:
                id_drone, name_zone = next(iter(d.items()))
                if name_zone == self.end["name"]:
                    continue
            
                path = self.step(d)
                if path is None:
                    continue

                if self.move_shortest(d, path):
                    _, name_zone = next(iter(d.items()))
                    moved += 1
                    print(f"D{id_drone}-{name_zone}", end=" ")
                    yield d

            print()
            turn += 1
            for d in self.drones:
                id_drone, name_zone = next(iter(d.items()))
                if self.check_status(name_zone, "restricted"):
                    turn += 1
                    break
            
            self.reset_connection_turn()
            yield moved
        
        print("\nTotal turns : ", turn)
        return

    def step(
        self,
        drone
    ) -> Any:
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

        if len(visited) == 1:
            return None
        return visited

    def move_shortest(
        self,
        drone,
        path
    ) -> bool:
        actual: tuple[str, int]
        
        name_closest_end: str = self.get_closest_to_end_from_point(drone, path)
        if name_closest_end is None:
            return False
        for k, v in path.items():
            if k == name_closest_end:
                actual = (k, v)
                break

        while actual[1] != 1:
            parents = self.get_parent(actual, path)
            n_parents: int = len(parents)
            if n_parents == 0:
                return False

            for p in parents:
                actual = p
                if self.check_status(p[0], "priority"):
                    break

        if not self.check_capacity(actual[0]):
            return False
        
        if not self.update_pos(drone, actual):
            return False
        return True

    def get_closest_to_end_from_point(
        self,
        drone,
        true_path
    ) -> str:
        saved_connection = deepcopy(self.connection)
        false_connection = deepcopy(self.connection)
        for f_c in false_connection:
            f_c["connection_turn"] = 0
        
        self.connection = false_connection
        path = self.step(drone)

        if path is None:
            raise ValueError("Path not Found")

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

            for parent in parents:
                actual = parent
                if self.check_status(parent[0], "priority"):
                    break

        for p in true_path:
            if p == actual[0]:
                self.connection = saved_connection
                return actual[0]
        self.connection = saved_connection
        return None

    def update_pos(self, drone: dict, pos: tuple[str, int]) -> bool:
        id_drone, pos_drone = next(iter(drone.items()))
        connection = self.get_connection(pos_drone, pos[0])
        if connection["connection_turn"] + 1 > connection["max_link_capacity"]:
            return False
        connection["connection_turn"] += 1

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
        return True

    def reset_connection_turn(self) -> None:
        for c in self.connection:
            c["connection_turn"] = 0

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
        if name == self.start["name"]:
            return self.start["meta"]["actual_drones"] + 1 <=  self.start["meta"]["max_drones"]
        if name == self.end["name"]:
            return self.end["meta"]["actual_drones"] + 1 <=  self.end["meta"]["max_drones"]

        for h in self.hub:
            if h["name"] == name:
                return h["meta"]["actual_drones"] + 1 <= h["meta"]["max_drones"]

        return False

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
        neighbors: list = []
        for b in self.belonging:
            for k, v in b.items():
                if k == name:
                    neighbors = v
                    break

        filtered_neighbors: list = []
        for n in neighbors:
            connection = self.get_connection(name, n)
            if connection["connection_turn"] < connection["max_link_capacity"]:
                filtered_neighbors.append(n)

        return filtered_neighbors
    
    
    def get_connection(
        self,
        con_1: str,
        con_2: str
    ) -> Any: 
        for c in self.connection:
            if c["1"] == con_1 and c["2"] == con_2:
                return c
            if c["2"] == con_1 and c["1"] == con_2:
                return c
        
        return None