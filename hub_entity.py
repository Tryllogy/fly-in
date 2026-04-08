from typing import Any
from ursina import (Entity, Vec3, color, Text)


class HubEntity(Entity):
    """Render a hub with a label in the scene."""

    def __init__(
        self,
            pos_x: int,
            pos_y: int,
            color_point: Any,
            texture: str,
            name: str,
            type_zone: str
    ) -> None:
        """Initialize the hub entity.

        Args:
            pos_x: X-axis world position.
            pos_y: Z-axis world position.
            color_point: Hub color object.
            texture: Texture name.
            name: Hub name.
            type_zone: Zone type string.
        """
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
        """Create a billboard label showing name and zone type."""
        self.label: Text = Text(
            parent=self,
            text=f"{self.name} [{self.type_zone}]",
            scale=8,
            position=Vec3(-1, 1, 0),
            billboard=True,
            color=color.white
        )
