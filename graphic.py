from entities import drone_entity, hub_entity
from ursina import (Entity, Vec3, color,
                    Mesh, BoxCollider, DirectionalLight, Sky)
from ursina.prefabs.first_person_controller import FirstPersonController
from drone import Drone
from typing import Generator, Any


class Graphic:
    def next_input(self, key: str) -> None:
        if key == 'escape':
            quit()

        if key == "n":
            drone_entity.DroneEntity.add_turn()

    def input(self, key: str) -> None:
        if key == 'escape':
            quit()

    def get_texture(
        self,
        hub: dict[str, Any]
    ) -> str:
        if hub["meta"]["color"] == "rainbow":
            return "rainbow"
        else:
            return "brick"

    def get_color(
        self,
        color_str: str
    ) -> Any:
        if (hasattr(color, color_str)):
            return getattr(color, color_str)
        else:
            return color.white

    def set_connections(
        self,
        space: int,
        drones: Drone
    ) -> None:

        for c in drones.connection:
            vertices: list[Vec3] = []
            zone_1: str = str(c["1"])
            zone_2: str = str(c["2"])

            if zone_1 == "start":
                pos_zone_1: tuple[int, int] = drones.start["position"]
                pos_zone_2: tuple[int, int] = [hub["position"]
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

    def set_ground(self, scale: int) -> None:
        Entity(
            model='plane',
            collider='box',
            scale=scale,
            texture='grass',
            texture_scale=(4, 4)
        )

    def set_player(self) -> None:
        player: FirstPersonController = FirstPersonController(
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
        self,
        space: int,
        start: dict[str, Any]
    ) -> hub_entity.HubEntity:
        pos_x: int = int(start["position"][0]) * space
        pos_y: int = int(start["position"][1]) * space
        name: str = str(start["name"])
        color_point: Any = self.get_color(str(
            start["meta"]["color"]))
        texture: str = self.get_texture(start)

        return hub_entity.HubEntity(
            pos_x=pos_x,
            pos_y=pos_y,
            color_point=color_point,
            texture=texture,
            name=name,
            type_zone=str(start["meta"]["zone"])
        )

    def set_end(
        self,
        space: int,
        end: dict[str, Any]
    ) -> hub_entity.HubEntity:
        pos_x: int = int(end["position"][0]) * space
        pos_y: int = int(end["position"][1]) * space
        name: str = str(end["name"])
        color_point: Any = self.get_color(
            str(end["meta"]["color"]))
        texture: str = self.get_texture(end)

        return hub_entity.HubEntity(
            pos_x=pos_x,
            pos_y=pos_y,
            color_point=color_point,
            texture=texture,
            name=name,
            type_zone=str(end["meta"]["zone"])
        )

    def set_hubs(
        self,
        start: hub_entity.HubEntity,
        end: hub_entity.HubEntity,
        space: int,
        drones: Drone
    ) -> list[hub_entity.HubEntity]:
        hub_entities: list[hub_entity.HubEntity] = [start, end]
        for h in drones.hub:
            pos_x: int = int(h["position"][0]) * space
            pos_y: int = int(h["position"][1]) * space
            color_point: Any = self.get_color(
                str(h["meta"]["color"]))
            texture: str = self.get_texture(h)
            hub_entities.append(hub_entity.HubEntity(pos_x=pos_x,
                                                     pos_y=pos_y,
                                                     color_point=color_point,
                                texture=texture,
                                name=str(h["name"]),
                                type_zone=str(h["meta"]["zone"])))

        return hub_entities

    def set_drones(
        self,
        drones: Drone,
        hubs: list[hub_entity.HubEntity]
    ) -> list[drone_entity.DroneEntity]:
        drones_entities: list[drone_entity.DroneEntity] = []
        for i in range(drones.n_drones):
            drones_entities.append(drone_entity.DroneEntity(
                i + 1,
                int(drones.start["position"][0]),
                int(drones.start["position"][1]),
                hubs))

        return drones_entities

    def set_sky(self) -> None:
        sun: DirectionalLight = DirectionalLight()
        sun.look_at(Vec3(1, -1, -1))
        Sky()

    def get_turns(
        self,
        drones: Drone,
        start: hub_entity.HubEntity
    ) -> dict[int, list[dict[int, str]]]:
        movements: Generator[Any, None, None] = drones.move_drones()
        all_movements: list[dict[int, str]] = []
        turn: int = 1
        turns: dict[int, list[dict[int, str]]] = {0: []}
        for drone in drones.drones:
            id_drone, name = next(iter(drone.items()))
            copy: dict[int, str] = {id_drone: start.name}
            turns[0].append(copy)
        while True:
            try:
                drone_item: dict[int, str] | int = next(movements)
                if isinstance(drone_item, dict):
                    id_drone, zone_name = next(iter(drone_item.items()))
                    copy = {id_drone: zone_name}
                    all_movements.append(copy)
                else:
                    turns.update({turn: all_movements.copy()})
                    turn += 1
                    all_movements.clear()
            except StopIteration:
                break

        return turns
