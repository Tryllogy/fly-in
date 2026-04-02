from ursina import (Entity, Vec3, color)

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