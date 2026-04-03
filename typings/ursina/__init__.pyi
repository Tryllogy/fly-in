from typing import Any

class _Color:
    white: Any
    white33: Any
    red: Any
    turquoise: Any
    gray: Any
    black66: Any
    orange: Any

class Vec3:
    x: float
    y: float
    z: float
    def __init__(self, x: float = ..., y: float = ..., z: float = ...) -> None: ...
    def __sub__(self, other: Vec3) -> Vec3: ...
    def length(self) -> float: ...

class Entity:
    position: Vec3
    name: str
    collider: Any
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def animate_position(self, position: Vec3, duration: float = ..., curve: Any = ...) -> None: ...

class Mesh:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class BoxCollider:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class DirectionalLight(Entity):
    def look_at(self, target: Vec3) -> None: ...

class Sky(Entity):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Text(Entity):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Ursina:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def run(self) -> None: ...

class _Curve:
    linear: Any

color: _Color
curve: _Curve
