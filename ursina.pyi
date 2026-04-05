from typing import Any

class FirstPersonController(Entity):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Vec3:
    x: float
    y: float
    z: float

    def __init__(self, x: float = ..., y: float = ..., z: float = ...) -> None: ...
    def __sub__(self, other: "Vec3") -> "Vec3": ...
    def length(self) -> float: ...


class Entity:
    position: Vec3
    collider: Any

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def animate_position(
        self,
        value: Vec3,
        duration: float = ...,
        curve: Any = ...,
    ) -> None: ...


class Text(Entity):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...


class Mesh:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...


class BoxCollider:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...


class DirectionalLight(Entity):
    def look_at(self, value: Vec3) -> None: ...


class Sky(Entity):
    pass


class Ursina:
    def run(self) -> None: ...


color: Any
curve: Any
