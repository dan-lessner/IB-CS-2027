import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Anna"

    def PickMove(self, auto, world, targets, validity):
        if targets is None or len(targets) == 0:
            return None

        has_velocity = auto.vel.vx != 0 or auto.vel.vy != 0

        # definice skupin pohybů
        forward_cone = [4, 7, 5, 8, 6]     # rovně + dopředné směry
        turns = [3, 1, 0, 2]               # zatáčky / úhyby

        # spočti kolik forward možností je validních
        valid_forward = 0
        i = 0
        while i < len(forward_cone):
            idx = forward_cone[i]
            if idx < len(targets):
                if validity is None or (idx < len(validity) and validity[idx]):
                    valid_forward += 1
            i += 1

        # 🔥 KLÍČ:
        # když je málo dopředných možností → jsme u zdi → radši zatoč
        if has_velocity and valid_forward <= 2:
            move_priority = turns + forward_cone
        else:
            if has_velocity:
                move_priority = [7, 5, 8, 4, 6, 3, 1, 0, 2]
            else:
                move_priority = [7, 5, 8, 4, 6, 3, 1, 0, 2]

        # vyber první validní
        i = 0
        while i < len(move_priority):
            idx = move_priority[i]
            if idx < len(targets):
                if validity is None or (idx < len(validity) and validity[idx]):
                    return targets[idx]
            i += 1

        # fallback
        if validity is not None:
            i = 0
            while i < len(validity):
                if validity[i] and i < len(targets):
                    return targets[i]
                i += 1

        return targets[0]
