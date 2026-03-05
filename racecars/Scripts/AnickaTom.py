import random
from simulation.script_api import AutoAuto
from simulation.game_state import Vertex

class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.last_positions = []
        self.direction = (1, 0)  # start moving right

    def GetName(self) -> str:
        return "AnickaTom"

    def _rotate_left(self, dx, dy):
        return (-dy, dx)

    def _rotate_right(self, dx, dy):
        return (dy, -dx)

    def _get_forward(self):
        return self.direction

    def _get_possible_moves(self):
        # forward, left, right (priority order)
        dx, dy = self.direction
        return [
            (dx, dy),              # forward
            self._rotate_left(dx, dy),
            self._rotate_right(dx, dy)
        ]

    def PickMove(self):
        # ensure position is initialized
        if not hasattr(self, "position") or self.position is None:
            return Vertex(0, 0)  # fallback start position

        x, y = self.position

        # remember history (to avoid loops)
        self.last_positions.append((x, y))
        if len(self.last_positions) > 10:
            self.last_positions.pop(0)

        # 1) Try preferred directions first
        for dx, dy in self._get_possible_moves():
            new_x = x + dx
            new_y = y + dy

            if (new_x, new_y) in self.last_positions:
                continue

            if self.IsValidPosition(new_x, new_y):
                self.direction = (dx, dy)
                return Vertex(new_x, new_y)

        # 2) Try any direction if blocked
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        random.shuffle(directions)
        for dx, dy in directions:
            new_x = x + dx
            new_y = y + dy
            if self.IsValidPosition(new_x, new_y):
                self.direction = (dx, dy)
                return Vertex(new_x, new_y)

        # 3) Absolute last resort: stay in place
        return Vertex(x, y)
