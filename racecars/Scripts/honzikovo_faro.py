import math
import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self):
        super().__init__()

    def GetName(self) -> str:
        return "honzikovo_faro"

    def PickMove(self, auto, world, targets, validity):
        if not targets or not validity:
            return None

        best_move = None
        best_dist = None

        for i in range(min(len(targets), len(validity))):
            if not validity[i]:
                continue

            move = targets[i]

        
            if move.x == auto.pos.x and move.y == auto.pos.y:
                continue

            dx = move.x - auto.pos.x
            dy = move.y - auto.pos.y
            dist = math.sqrt(dx * dx + dy * dy)

            if best_dist is None or dist > best_dist:
                best_dist = dist
                best_move = move

        if best_move is not None:
            return best_move


        valid_moves = []
        for i in range(min(len(targets), len(validity))):
            if validity[i]:
                valid_moves.append(targets[i])

        if len(valid_moves) == 0:
            return auto.pos

        return random.choice(valid_moves)