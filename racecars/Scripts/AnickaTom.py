import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "AnickaTom"

    def PickMove(self, auto, world, targets, validity):
        # Make the car move forward
        if targets is None:
            return None
        if len(targets) == 0:
            return None
        
        # Check if car has velocity
        has_velocity = auto.vel.vx != 0 or auto.vel.vy != 0

        # 🔁 místo jednoho směru teď máme PRIORITY pohybů
        if has_velocity:
            # preferujeme udržet směr, ale dovolíme i zatáčení
            move_priority = [4, 7, 5, 8, 6, 3, 1, 0, 2]
        else:
            # když stojíme, zkusíme se rozjet různými směry
            move_priority = [7, 5, 8, 4, 6, 3, 1, 0, 2]

        # 🔍 vyber první validní move podle priority
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
        return targets[0] if len(targets) > 0 else None
