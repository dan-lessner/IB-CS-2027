import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self):
        self.last_move = None  # paměť posledního tahu

    def GetName(self) -> str:
        return "Anna"

    def PickMove(self, auto, world, targets, validity):
        if targets is None or len(targets) == 0:
            return None

        # mapa opačných směrů (abychom se nevraceli)
        opposite = {
            0: 8, 1: 7, 2: 6,
            3: 5, 4: None, 5: 3,
            6: 2, 7: 1, 8: 0
        }

        best_target = None
        best_score = -999999

        i = 0
        while i < len(targets):
            if validity is None or (i < len(validity) and validity[i]):

                score = 0

                # ❌ nevracej se zpátky
                if self.last_move is not None and opposite.get(self.last_move) == i:
                    score -= 100

                # ✔️ preferuj pokračování stejným směrem
                if self.last_move is not None and i == self.last_move:
                    score += 5

                # ✔️ preferuj lehké zatáčky (sousední indexy)
                if self.last_move is not None and abs(i - self.last_move) == 1:
                    score += 2

                # 👉 jemný bias doprava (k cíli)
                if i in [7, 8, 6]:
                    score += 1.5
                if i in [0, 1, 2]:
                    score -= 1

                # trocha randomness, aby se nezaseklo
                score += random.random() * 0.3

                if score > best_score:
                    best_score = score
                    best_target = targets[i]
                    best_index = i

            i += 1

        if best_target is not None:
            self.last_move = best_index
            return best_target

        # fallback
        return targets[0]
