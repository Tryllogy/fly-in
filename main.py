from drone import Drone
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import sys
import math


class DroneEntity(Entity):
    turn: int = 0
    max_turn: int = 0
    def __init__(self, drone_id: int, pos_x: int, pos_y: int, hubs):
        super().__init__(
            position=Vec3(pos_x, 2, pos_y),
            collider='box'
        )

        self.body = Entity(
            parent=self,
            model='cube',
            scale=Vec3(0.45, 0.14, 0.28),
            color=color.turquoise,
            y=0
        )

        self.arm_x = Entity(
            parent=self,
            model='cube',
            scale=Vec3(0.8, 0.04, 0.04),
            color=color.gray
        )

        self.arm_z = Entity(
            parent=self,
            model='cube',
            scale=Vec3(0.04, 0.04, 0.8),
            color=color.gray
        )

        rotor_scale = Vec3(0.12, 0.02, 0.12)
        rotor_height = 0.06
        rotor_offsets = [
            Vec3(0.36, rotor_height, 0.36),
            Vec3(0.36, rotor_height, -0.36),
            Vec3(-0.36, rotor_height, 0.36),
            Vec3(-0.36, rotor_height, -0.36),
        ]

        self.rotors = [
            Entity(parent=self, model='cube', scale=rotor_scale, position=offset, color=color.black66)
            for offset in rotor_offsets
        ]

        self.pos_x: int = pos_x
        self.pos_y: int = pos_y
        self.drone_id: int = drone_id
        self.movements: list = []
        self.hubs = hubs
        self.last_applied_turn: int = -1
        self.move_duration: float = 0.5
    
    def move_to_hub(self, hub_pos, duration=0.35):
        self.animate_position(
            Vec3(hub_pos.x, 2, hub_pos.z),
            duration=duration,
            curve=curve.linear
        )
    
    def update(self) -> None:
        if self.last_applied_turn == DroneEntity.turn:
            return

        hub_name: str = None
        for t_id, turn in self.all_turns.items():
            if t_id != DroneEntity.turn:
                continue

            for t in turn:
                id_drone, zone = next(iter(t.items()))
                if id_drone != self.drone_id:
                    continue
                else:
                    hub_name = zone

        if hub_name is None:
            self.last_applied_turn = DroneEntity.turn
            return

        for h in self.hubs:
            if h.name == hub_name:
                target: Vec3 = Vec3(h.position.x, 2, h.position.z)
                if (self.position - target).length() > 0.001:
                    self.move_to_hub(h.position, self.move_duration)
                self.last_applied_turn = DroneEntity.turn
                break
                
    @classmethod
    def add_turn(cls) -> None:
        if cls.turn == cls.max_turn:
            return
        cls.turn += 1
        
    @classmethod
    def remove_turn(cls) -> None:
        if cls.turn == 0:
            return
        cls.turn -= 1
        
    @classmethod
    def set_max_turn(cls, all_turns) -> None:
        max_turn: int = list(all_turns.keys())[-1]
        cls.max_turn = max_turn


class HubEntity(Entity):
    def __init__(self, pos_x: int, pos_y: int, color_point: color, texture: str, name: str):
        super().__init__(
            model='cube',
            scale=0.5,
            texture=texture,
            texture_scale=(1, 2),
            position=Vec3(
                pos_x,
                0.3,
                pos_y
            ),
            collider='box',
            color=color_point
            )
        self.name = name
    

def next_input(key) -> None:
    if key == 'escape':
        quit()

    if key == "n":
        DroneEntity.add_turn()

    if key == "p":
        DroneEntity.remove_turn()


def input(key):
    if key == 'escape':
        quit()



def get_texture(
    hub: dict[str, str | tuple[int, int] | dict[str, str | int]]
) -> str:
    if hub["meta"]["color"] == "rainbow":
        return "rainbow"
    else:
        return "brick"


def get_color(
    color_str: str
) -> color:
    if (hasattr(color, color_str)):
        return getattr(color, color_str)
    else:
        return color.white


def set_connections(
    space: int,
    drones: Drone
) -> None:

    for c in drones.connection:
        vertices: list = []
        zone_1: str = c["1"]
        zone_2: str = c["2"]

        if zone_1 == "start":
            pos_zone_1 = drones.start["position"]
            pos_zone_2 = [hub["position"]
                          for hub in drones.hub
                          if hub["name"] == zone_2][0]

        else:
            pos_zone_1 = [hub["position"]
                          for hub in drones.hub
                          if hub["name"] == zone_1][0]
            if "goal" in zone_2:
                pos_zone_2 = drones.end["position"]
            else:
                pos_zone_2 = [hub["position"]
                              for hub in drones.hub
                              if hub["name"] == zone_2][0]

        pos_x: int = pos_zone_1[0] * space
        pos_y: int = pos_zone_1[1] * space
        vertices.append(Vec3(pos_x, 0.2, pos_y))

        pos_x = pos_zone_2[0] * space
        pos_y = pos_zone_2[1] * space
        vertices.append(Vec3(pos_x, 0.2, pos_y))

        Entity(
            model=Mesh(vertices=vertices, mode="line", thickness=5),
            color=color.white
        )


def set_ground(scale: int):
    Entity(
        model='plane',
        collider='box',
        scale=scale,
        texture='grass',
        texture_scale=(4, 4)
    )


def set_player() -> None:
    player: FirstPersonController = FirstPersonController(
        model='cube',
        z=-10,
        color=color.orange,
        origin_y=-.5,
        speed=20,
        collider='box',
        gravity=0,
        y=2,
        ignore_paused=True
    )
    player.collider = BoxCollider(
        player,
        Vec3(0, 1, 0),
        Vec3(1, 2, 1)
    )


def set_spawn(
    space: int,
    start: dict[str, str | tuple[int, int]
                | dict[str, str | int]]
) -> None:
    pos_x: int = start["position"][0] * space
    pos_y: int = start["position"][1] * space
    name: str = start["name"]
    color_point: color = get_color(start["meta"]["color"])
    texture: str = get_texture(start)

    return HubEntity(
        pos_x=pos_x,
        pos_y=pos_y,
        color_point=color_point,
        texture=texture,
        name=name
        )


def set_end(
    space: int,
    end: dict[str, str | tuple[int, int]
              | dict[str, str | int]]
) -> None:
    pos_x = end["position"][0] * space
    pos_y = end["position"][1] * space
    name: str = end["name"]
    color_point: color = get_color(end["meta"]["color"])
    texture: str = get_texture(end)

    return HubEntity(
        pos_x=pos_x,
        pos_y=pos_y,
        color_point=color_point,
        texture=texture,
        name=name
        )


def set_hubs(start, end, space: int, drones) -> list:
    hub_entities: list = [start, end]
    for h in drones.hub:
        pos_x: int = h["position"][0] * space
        pos_y: int = h["position"][1] * space
        color_point: color = get_color(h["meta"]["color"])
        texture: str = get_texture(h)
        hub_entities.append(HubEntity(pos_x=pos_x, pos_y=pos_y, color_point=color_point, texture=texture, name=h["name"]))
    
    return hub_entities

def set_drones(drones, hubs) -> list:
    drones_entities: list[DroneEntity] = []
    for i in range(drones.n_drones):
        drones_entities.append(DroneEntity(i + 1, drones.start["position"][0], drones.start["position"][1], hubs))

    return drones_entities

def set_sky() -> None:
    sun: DirectionalLight = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()


def get_turns(drones, start) -> list:
    movements: Generator = drones.move_drones()
    all_movements: list[dict] = []
    turn: int = 1
    turns: dict = {0: []}
    for drone in drones.drones:
        id_drone, name = next(iter(drone.items()))
        copy = {id_drone: start.name}
        turns[0].append(copy)
    while 1:
        try:
            drone: dict | int = next(movements)
            if isinstance(drone, dict):
                id_drone, zone_name = next(iter(drone.items()))
                copy = {id_drone: zone_name}
                all_movements.append(copy)
            else:
                turns.update({turn: all_movements.copy()})
                turn += 1
                all_movements.clear()
        except StopIteration as e:
            break

    return turns



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
        Entity.default_shader = lit_with_shadows_shader
        space: int = 3

        set_sky()
        set_ground(max((len(drones.hub) + 2) * 3, 30))
        set_player()
        start: Entity = set_spawn(space, drones.start)
        end: Entity = set_end(space, drones.end)
        hub_entities: list = set_hubs(start, end, space, drones)
        set_connections(space, drones)
        drones_entities: list = set_drones(drones, hub_entities)
        
        all_turns: dict = get_turns(drones, start)
        for d in drones_entities:
            d.all_turns = all_turns
        DroneEntity.set_max_turn(all_turns)
        pause_handler = Entity(ignore_paused=True, input=next_input)
        app.run()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
