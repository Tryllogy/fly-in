from typing import Any
from ursina import (Entity, Vec3, color, Text)


class HubEntity(Entity):
    def __init__(
        self,
            pos_x: int,
            pos_y: int,
            color_point: Any,
            texture: str,
            name: str,
            type_zone: str
    ) -> None:
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
        self.name: str = name
        self.type_zone: str = type_zone
        self.create_text()

    def create_text(self) -> None:
        self.label: Text = Text(
            parent=self,
            text=f"{self.name} [{self.type_zone}]",
            scale=8,
            position=Vec3(-1, 1, 0),
            billboard=True,
            color=color.white
        )
