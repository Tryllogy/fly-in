from typing import Any


class Vec3:
    """3D vector stub."""

    x: float
    y: float
    z: float

    def __init__(self, x: float = ..., y: float = ..., z: float = ...) -> None: ...
    def __sub__(self, other: "Vec3") -> "Vec3": ...
    def length(self) -> float: ...


class Entity:
    """Base entity stub."""

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
    """Text entity stub."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...


class Mesh:
    """Mesh stub."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...


class BoxCollider:
    """Box collider stub."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...


class DirectionalLight(Entity):
    """Directional light stub."""

    def look_at(self, value: Vec3) -> None: ...


class Sky(Entity):
    """Sky entity stub."""

    pass


class Ursina:
    """Application stub."""

    def run(self) -> None: ...


color: Any
curve: Any
