import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):

    def __init__(self, track):
        super().__init__()
        self.last_positions = []
        self.direction = (1, 0)

    def GetName(self) -> str:
        return "AnickaTom"

    def PickMove(self, auto, world, targets, validity):
        # dafuq tady nemuze byt zadnej possible move
        if not targets:
            return None

        current_x = auto.pos.x
        current_y = auto.pos.y

        # posledni pozice pamatujeme...
        self.last_positions.append((current_x, current_y))
        if len(self.last_positions) > 8:
            self.last_positions.pop(0)

        # jestli se zasekne detekce
        stuck = False
        if len(self.last_positions) == 8:
            xs = [p[0] for p in self.last_positions]
            ys = [p[1] for p in self.last_positions]

            if (max(xs) - min(xs) < 2) and (max(ys) - min(ys) < 2):
                stuck = True

        # move pool
        valid_moves = []
        for i in range(len(targets)):
            if validity is None or (i < len(validity) and validity[i]):
                valid_moves.append((targets[i], i))

        pool = valid_moves if valid_moves else [(targets[i], i) for i in range(len(targets))]

        # jedeme dopredu
        forward_blocked = True
        for move, i in valid_moves:
            if move.x > current_x:
                forward_blocked = False
                break

        # juchu move
        best_move = None
        best_score = float("-inf")

        for move, idx in pool:
            dx = move.x - current_x
            dy = move.y - current_y

            if dx == 0 and dy == 0:
                continue

            if stuck:
                score = abs(dx) + abs(dy) + random.uniform(0, 2)

            else:
                momentum_bonus = 3 if (dx, dy) == self.direction else 0
                diagonal_bonus = 1.5 if abs(dx) > 0 and abs(dy) > 0 else 0

                if forward_blocked:
                    score = abs(dx) + abs(dy) * 2
                else:
                    score = (dx * 4) - (abs(dy) * 0.5)

                score += momentum_bonus + diagonal_bonus
                score += random.uniform(0, 0.2)

            if score > best_score:
                best_score = score
                best_move = move
                self.direction = (dx, dy)

        if best_move is None:
            return targets[0]

        return best_move
