from typing import Any
from ursina import Entity

class FirstPersonController(Entity):
    collider: Any
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
