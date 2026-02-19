import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "Anna"

    def PickMove(self, auto, world, targets, validity):
        if targets is None or len(targets) == 0:
            return None

        # má auto rychlost?
        has_velocity = auto.vel.vx != 0 or auto.vel.vy != 0

        # ❗ KLÍČOVÁ ZMĚNA:
        # forward (4) už není první, jinak nikdy nezatočíš
        if has_velocity:
            move_priority = [7, 5, 8, 6, 3, 1, 4, 0, 2]
        else:
            move_priority = [7, 5, 8, 4, 6, 3, 1, 0, 2]

        # vyber první validní move podle priority
        i = 0
        while i < len(move_priority):
            idx = move_priority[i]
            if idx < len(targets):
                if validity is None or (idx < len(validity) and validity[idx]):
                    return targets[idx]
            i += 1

        # fallback: první validní
        if validity is not None:
            i = 0
            while i < len(validity):
                if validity[i] and i < len(targets):
                    return targets[i]
                i += 1

        # úplný fallback
        re
