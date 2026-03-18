import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self, logger=None):
        super().__init__(logger)
        self.history = []

    def GetName(self) -> str:
        return "honzikovo_faro"

    def PickMove(self, auto, world, targets, validity):
        if not targets or not validity:
            return None

        # build list of valid moves, just that
        allowed_moves = []
        for i in range(min(len(targets), len(validity))):
            if validity[i]:
                if not (targets[i].x == auto.pos.x and targets[i].y == auto.pos.y):
                    allowed_moves.append(targets[i])

        # If only staying is valid, return the first valid move.
        if len(allowed_moves) == 0:
            for i in range(min(len(targets), len(validity))):
                if validity[i]:
                    return targets[i]
            return auto.pos

        # track recent positions to avoid lops
        coords = (auto.pos.x, auto.pos.y)
        repeat = coords in self.history
        self.history.append(coords)
        if len(self.history) > 4:
            self.history.pop(0)

        if repeat and len(allowed_moves) > 1:
            return random.choice(allowed_moves)

       
        return allowed_moves[-1]
