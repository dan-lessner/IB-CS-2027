import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Anna"

    def _get_turn_options(self, vx, vy):
        # Determine turn options based on current velocity
        if vx > 0:  # moving right
            return [5, 3, 8, 6, 2, 0]
        elif vx < 0:  # moving left
            return [5, 3, 2, 0, 8, 6]
        elif vy > 0:  # moving down
            return [7, 1, 8, 2, 6, 0]
        elif vy < 0:  # moving up
            return [7, 1, 6, 0, 8, 2]
        else:
            return [7, 5, 8, 1, 3, 6, 2, 0]

    def PickMove(self, auto, world, targets, validity):
        if targets is None or len(targets) == 0:
            return None

        vx = auto.vel.vx
        vy = auto.vel.vy
        has_velocity = vx != 0 or vy != 0

        def is_valid(i):
            return validity is None or (i < len(validity) and validity[i])

        # =========================
        # CASE 1: CAR IS MOVING
        # =========================
        if has_velocity:
            forward_index = 4

            # try going forward first
            if forward_index < len(targets) and is_valid(forward_index):
                return targets[forward_index]

            # forward blocked → turn!
            turn_options = self._get_turn_options(vx, vy)

            # shuffle to avoid infinite deterministic loops
            random.shuffle(turn_options)

            for idx in turn_options:
                if idx < len(targets) and is_valid(idx):
                    return targets[idx]

        # =========================
        # CASE 2: CAR IS STOPPED
        # =========================
        else:
            start_options = [7, 5, 1, 3, 8, 6, 2, 0]
            random.shuffle(start_options)

            for idx in start_options:
                if idx < len(targets) and is_valid(idx):
                    return targets[idx]

        # =========================
        # LAST RESORT: ANY VALID MOVE
        # =========================
        for i in range(len(targets)):
            if is_valid(i):
                return targets[i]

        return None