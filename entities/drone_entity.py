from ursina import (Entity, Vec3, color, curve,
                    Text)

class DroneEntity(Entity):
    turn: int = 0
    max_turn: int = 0
    def __init__(self, drone_id: int, pos_x: int, pos_y: int, hubs):
        super().__init__(
            position=Vec3(pos_x, 2, pos_y),
            collider='box'
        )
        self.create_body()
        self.drone_id: int = drone_id
        self.add_name()
        self.movements: list = []
        self.hubs = hubs
        self.last_applied_turn: int = -1
        self.move_duration: float = 0.5


    def move_to_hub(self, hub_pos, duration=0.35):
        self.animate_position(
            Vec3(hub_pos.x, 2, hub_pos.z),
            duration=duration,
            curve=curve.linear
        )
    
    def add_name(self):
        self.label = Text(
            parent=self,
            text=f"Drone {self.drone_id}",
            position=Vec3(-0.37, 1.2, 0),
            scale=8,
            billboard=True,
            color=color.red
        )
    
    def create_body(self):
        self.body = Entity(
            parent=self,
            model='cube',
            scale=Vec3(0.45, 0.14, 0.28),
            color=color.turquoise,
            y=0
        )

        self.arm_x = Entity(
            parent=self,
            model='cube',
            scale=Vec3(0.8, 0.04, 0.04),
            color=color.gray
        )

        self.arm_z = Entity(
            parent=self,
            model='cube',
            scale=Vec3(0.04, 0.04, 0.8),
            color=color.gray
        )

        rotor_scale = Vec3(0.12, 0.02, 0.12)
        rotor_height = 0.06
        rotor_offsets = [
            Vec3(0.36, rotor_height, 0.36),
            Vec3(0.36, rotor_height, -0.36),
            Vec3(-0.36, rotor_height, 0.36),
            Vec3(-0.36, rotor_height, -0.36),
        ]

        self.rotors = [
            Entity(parent=self, model='cube', scale=rotor_scale, position=offset, color=color.black66)
            for offset in rotor_offsets
        ]
    
    def update(self) -> None:
        if self.last_applied_turn == DroneEntity.turn:
            return

        hub_name: str = None
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
        if cls.turn == cls.max_turn:
            return
        cls.turn += 1

    @classmethod
    def set_max_turn(cls, all_turns) -> None:
        max_turn: int = list(all_turns.keys())[-1]
        cls.max_turn = max_turn
