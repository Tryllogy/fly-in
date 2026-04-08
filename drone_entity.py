from ursina import (Entity, Vec3, color, curve,
                    Text)
from hub_entity import HubEntity


class DroneEntity(Entity):
    """Render and animate a drone in the simulation.

    Attributes:
        turn: Current global simulation turn displayed by entities.
        max_turn: Maximum available turn for playback.
    """

    turn: int = 0
    max_turn: int = 0

    def __init__(
            self,
            drone_id: int,
            pos_x: int,
            pos_y: int,
            hubs: list[HubEntity]
    ) -> None:
        """Initialize a drone entity with visual components.

        Args:
            drone_id: Identifier of the drone.
            pos_x: Initial x-axis grid position.
            pos_y: Initial y-axis grid position.
            hubs: Available hub entities used for movements.
        """
        super().__init__(
            position=Vec3(pos_x, 2, pos_y),
            collider='box'
        )
        self.create_body()
        self.drone_id: int = drone_id
        self.add_name()
        self.movements: list[dict[int, str]] = []
        self.hubs: list[HubEntity] = hubs
        self.last_applied_turn: int = -1
        self.move_duration: float = 0.5
        self.all_turns: dict[int, list[dict[int, str]]] = {}
        self.activated: bool = False

    def move_to_hub(
        self,
        hub_pos: Vec3,
        duration: float = 0.35
    ) -> None:
        """Animate the drone to a target hub position.

        Args:
            hub_pos: Target hub position in world coordinates.
            duration: Animation duration in seconds.
        """
        self.animate_position(
            Vec3(hub_pos.x, 2, hub_pos.z),
            duration=duration,
            curve=curve.linear
        )

    def add_name(self) -> None:
        """Attach a billboard text label to the drone."""
        self.label: Text = Text(
            parent=self,
            text=f"Drone {self.drone_id}",
            position=Vec3(-0.37, 1.2, 0),
            scale=8,
            billboard=True,
            color=color.red
        )

    def create_body(self) -> None:
        """Create body, arms, and rotors for the drone model."""
        self.body: Entity = Entity(
            parent=self,
            model='cube',
            scale=Vec3(0.45, 0.14, 0.28),
            color=color.turquoise,
            y=0
        )

        self.arm_x: Entity = Entity(
            parent=self,
            model='cube',
            scale=Vec3(0.8, 0.04, 0.04),
            color=color.gray
        )

        self.arm_z: Entity = Entity(
            parent=self,
            model='cube',
            scale=Vec3(0.04, 0.04, 0.8),
            color=color.gray
        )

        rotor_scale: Vec3 = Vec3(0.12, 0.02, 0.12)
        rotor_height: float = 0.06
        rotor_offsets: list[Vec3] = [
            Vec3(0.36, rotor_height, 0.36),
            Vec3(0.36, rotor_height, -0.36),
            Vec3(-0.36, rotor_height, 0.36),
            Vec3(-0.36, rotor_height, -0.36),
        ]

        self.rotors: list[Entity] = [
            Entity(parent=self, model='cube', scale=rotor_scale,
                   position=offset, color=color.black66)
            for offset in rotor_offsets
        ]

    def update(self) -> None:
        """Apply movement for the current turn if needed."""
        if self.last_applied_turn == DroneEntity.turn:
            return

        hub_name: str | None = None
        for t_id, turn in self.all_turns.items():
            if t_id != DroneEntity.turn:
                continue

            for t in turn:
                id_drone, data = next(iter(t.items()))
                if id_drone != self.drone_id:
                    continue
                else:
                    hub_name = data[0]

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
        """Increment the global turn within bounds."""
        if cls.turn == cls.max_turn:
            return
        cls.turn += 1

    @classmethod
    def set_max_turn(cls, all_turns: dict[int, list[dict[int, str]]]) -> None:
        """Set the maximum playable turn from precomputed turns.

        Args:
            all_turns: Mapping of turn index to drone positions.
        """
        max_turn: int = list(all_turns.keys())[-1]
        cls.max_turn = max_turn
