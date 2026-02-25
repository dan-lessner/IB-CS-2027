import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Anna"

    def _get_turn_options(self, vx, vy):
        if vx > 0:  # right
            return [5, 3, 8, 6, 2, 0]
        elif vx < 0:  # left
            return [5, 3, 2, 0, 8, 6]
        elif vy > 0:  # down
            return [7, 1, 8, 2, 6, 0]
        elif vy < 0:  # up
            return [7, 1, 6, 0, 8, 2]
        else:
            return [7, 5, 1, 3, 8, 6, 2, 0]

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None

        vx = auto.vel.vx
        vy = auto.vel.vy

        def is_valid(i):
            return validity is None or (i < len(validity) and validity[i])

        # =========================
        # 1. IF MOVING → try keep direction
        # =========================
        if vx != 0 or vy != 0:
            forward_index = 4  # keep velocity (0 acceleration)

            if forward_index < len(targets) and is_valid(forward_index):
                return targets[forward_index]

            # blocked → turn
            turn_options = self._get_turn_options(vx, vy)
            random.shuffle(turn_options)

            for idx in turn_options:
                if idx < len(targets) and is_valid(idx):
                    return targets[idx]

        # =========================
        # 2. IF STOPPED → MUST accelerate
        # =========================
        start_moves = [7, 5, 1, 3, 8, 6, 2, 0]  # everything except 4
        random.shuffle(start_moves)

        for idx in start_moves:
            if idx < len(targets) and is_valid(idx):
                return targets[idx]

        # =========================
        # 3. LAST RESORT
        # =========================
        for i in range(len(targets)):
            if is_valid(i):
                return targets[i]

        return None