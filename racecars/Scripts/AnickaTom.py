import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def GetName(self) -> str:
        return "AnickaTom"

    def PickMove(self, auto, world, targets, validity):
        if targets is None or len(targets) == 0:
            return None

        best_target = None
        best_score = -999999

        i = 0
        while i < len(targets):
            if validity is None or (i < len(validity) and validity[i]):
                t = targets[i]

                # rozdíl pozice = kam se posuneme
                dx = t.pos.x - auto.pos.x
                dy = t.pos.y - auto.pos.y

                # skóre = jak moc jdeme dopředu (větší = lepší)
                score = dx * dx + dy * dy

                # malý bonus za udržení směru (index 4), ale už není absolutní priorita
                if i == 4:
                    score += 0.1

                if score > best_score:
                    best_score = score
                    best_target = t

            i += 1

        if best_target is not None:
            return best_target

        # fallback
        if validity is not None:
            i = 0
            while i < len(validity):
                if validity[i] and i < len(targets):
                    return targets[i]
                i += 1

        return targets[0]
