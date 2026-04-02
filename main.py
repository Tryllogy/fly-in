from drone import Drone
from ursina import (Ursina, Entity)
from entities import drone_entity
from graphic import Graphic
import sys


def main() -> None:
    if len(sys.argv) == 1:
        print("Usage: python main.py <map_file>")
        return

    try:
        drones: Drone = Drone.from_file(sys.argv[1])
    except Exception as e:
        print(f"Error: {e}")

    try:
        app: Ursina = Ursina()
        space: int = 3
        graphic = Graphic()
        graphic.set_sky()
        graphic.set_ground(max((len(drones.hub) + 2) * 3, 30))
        graphic.set_player()
        start: Entity = graphic.set_spawn(space, drones.start)
        end: Entity = graphic.set_end(space, drones.end)
        hub_entities: list = graphic.set_hubs(start, end, space, drones)
        graphic.set_connections(space, drones)
        drones_entities: list = graphic.set_drones(drones, hub_entities)
        
        all_turns: dict = graphic.get_turns(drones, start)
        for d in drones_entities:
            d.all_turns = all_turns
        drone_entity.DroneEntity.set_max_turn(all_turns)
        _ = Entity(ignore_paused=True, input=graphic.next_input)
        app.run()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
