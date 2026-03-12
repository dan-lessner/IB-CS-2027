import random
from simulation.script_api import AutoAuto

class Auto(AutoAuto):
    def __init__(self, track) -> None: 
        super().__init__()
        self.last_positions = []
        self.visit_count = {}

    def GetName(self):
        return "Luci"

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None

        # --- Update visit memory ---
        pos = (auto.pos.x, auto.pos.y)
        self.visit_count[pos] = self.visit_count.get(pos, 0) + 1

        # --- Track last positions for stuck detection ---
        self.last_positions.append(pos)
        if len(self.last_positions) > 6:
            self.last_positions.pop(0)

        stuck = False
        if len(self.last_positions) == 6:
            xs = [p[0] for p in self.last_positions]
            ys = [p[1] for p in self.last_positions]
            if (max(xs) - min(xs) < 1) and (max(ys) - min(ys) < 1):
                stuck = True

        # --- Filter valid moves ---
        pool = [targets[i] for i in range(len(targets)) if validity[i]]
        if not pool:
            pool = list(targets)

        current_x = auto.pos.x
        current_y = auto.pos.y

        # --- Helper: visit score ---
        def score(move):
            return self.visit_count.get((move.x, move.y), 0)

        # --- 1. If stuck: choose the least-visited move, ignoring direction ---
        if stuck:
            return min(pool, key=score)

        # --- 2. Try to move forward only (x increasing) ---
        forward_moves = [m for m in pool if m.x > current_x]

        if forward_moves:
            # choose the forward tile with the lowest visit count
            return min(forward_moves, key=score)

        # --- 3. If no forward move exists, choose sideways but NEVER backwards ---
        sideways_moves = [m for m in pool if m.x == current_x]
        if sideways_moves:
            return min(sideways_moves, key=score)

        # --- 4. Absolute fallback: if only backward moves exist, pick the least visited ---
        # (This prevents the car from freezing completely.)
        return min(pool, key=score)