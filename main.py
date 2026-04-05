from drone import Drone
from ursina import (Ursina, Entity)
from drone_entity import DroneEntity
from graphic import Graphic
from hub_entity import HubEntity
import sys


def main() -> None:
    if len(sys.argv) == 1:
        print("Usage: python main.py <map_file>")
        return

    try:
        drones: Drone = Drone.from_file(sys.argv[1])
    except Exception as e:
        print(f"Error getting data: {e}")
        sys.exit()

    try:
        app: Ursina = Ursina()
        space: int = 3
        graphic: Graphic = Graphic(drones.start, drones.end)
        graphic.set_sky()
        graphic.set_ground(max((len(drones.hub) + 2) * 3, 60))
        graphic.set_player()
        start: HubEntity = graphic.set_spawn(space, drones.start)
        end: HubEntity = graphic.set_end(space, drones.end)
        hub_entities: list[HubEntity] = (
            graphic.set_hubs(start, end, space, drones)
        )
        graphic.set_connections(space, drones)
        drones_entities: list[DroneEntity] = (
            graphic.set_drones(drones, hub_entities)
        )

        all_turns: dict[int, list[dict[int, str]]] = (
            graphic.get_turns(drones, start)
        )
        for d in drones_entities:
            d.all_turns = all_turns
        DroneEntity.set_max_turn(all_turns)
        _ = Entity(ignore_paused=True, input=graphic.next_input)
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit()


if __name__ == "__main__":
    main()
