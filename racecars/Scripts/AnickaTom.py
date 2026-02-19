import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self):
        self.last_move = None
        self.visited = set()

    def GetName(self) -> str:
        return "Anna"

    def PickMove(self, auto, world, targets, validity):
        if targets is None or len(targets) == 0:
            return None

        current_pos = (auto.pos.x, auto.pos.y)
        self.visited.add(current_pos)

        opposite = {
            0: 8, 1: 7, 2: 6,
            3: 5, 4: None, 5: 3,
            6: 2, 7: 1, 8: 0
        }

        best_target = None
        best_score = -999999
        best_index = 0

        for i in range(len(targets)):
            if validity is not None and (i >= len(validity) or not validity[i]):
                continue

            t = targets[i]

            # tady MUSÍ být pos
            next_pos = (t.pos.x, t.pos.y)

            score = 0

            # n návrat do stejného místa
            if next_pos in self.visited:
                score -= 5

            # zákaz otočky
            if self.last_move is not None and opposite.get(self.last_move) == i:
                score -= 100

            # pokračuj stejným směrem
            if self.last_move is not None and i == self.last_move:
                score += 4

            # jemná zatáčka
            if self.last_move is not None and abs(i - self.last_move) == 1:
                score += 2

            # bias doprava (k cíli)
            if i in [7, 8, 6]:
                score += 2
            if i in [0, 1, 2]:
                score -= 1

            # malé random aby se nezacyklil
            score += random.random() * 0.2

            if score > best_score:
                best_score = score
                best_target = t
                best_index = i

        self.last_move = best_index
        return best_target
