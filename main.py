from drone import Drone
from ursina import (Ursina, Entity,
                    BoxCollider, color, DirectionalLight, Sky, Vec3, Mesh)
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import sys


def print_data(n_drones, start, end, hub, connection):
    print(n_drones)
    print()
    print(start)
    print()
    print(end)
    print()
    for h in hub:
        print(h)
    print()
    for c in connection:
        print(c)


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
        y=2
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
    color_point: color = get_color(start["meta"]["color"])
    texture: str = get_texture(start)

    Entity(model='cube',
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


def set_end(
    space: int,
    end: dict[str, str | tuple[int, int]
              | dict[str, str | int]]
) -> None:
    pos_x = end["position"][0] * space
    pos_y = end["position"][1] * space
    color_point: color = get_color(end["meta"]["color"])
    texture: str = get_texture(end)

    Entity(model='cube',
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


def set_hubs(
    space: int,
    hub: list[dict[str, str | tuple[int, int]
                   | dict[str, str | int]]]
) -> None:

    for h in hub:
        pos_x: int = h["position"][0] * space
        pos_y: int = h["position"][1] * space
        color_point: color = get_color(h["meta"]["color"])
        texture: str = get_texture(h)

        Entity(model='cube',
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


def set_sky() -> None:
    sun: DirectionalLight = DirectionalLight()
    sun.look_at(Vec3(1, -1, -1))
    Sky()


def set_drones(
    drones: Drone
) -> None:
    pos_x: int = drones.start["position"][0]
    pos_y: int = drones.start["position"][1]
    for i in range(drones.n_drones):
        Entity(model='sphere',
               scale=0.5,
               texture='rainbow',
               texture_scale=(1, 2),
               position=Vec3(
                   pos_x,
                   2,
                   pos_y
               ),
               collider='box',
               color=color.turquoise
               )


def main() -> None:
    if len(sys.argv) == 1:
        print("Usage: python main.py <map_file>")
        return

    try:
        drones: Drone = Drone.from_file(sys.argv[1])
        drones.set_map_dimension()
        drones.show_data()
    except Exception as e:
        print(f"Error: {e}")

    try:
        app: Ursina = Ursina()
        Entity.default_shader = lit_with_shadows_shader
        space: int = 3

        set_sky()
        set_ground(max(drones.n_drones * 7, 30))
        set_player()
        set_spawn(space, drones.start)
        set_end(space, drones.end)
        set_hubs(space, drones.hub)
        set_connections(space, drones)
        set_drones(drones)
        drones.move_drones()
            
        # drones.show_data()
        app.run()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
