import math
import random
from shutil import move
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.step = 0
        self.history = []
    
    def GetName(self) -> str:
        return "Fildy Driver"

    def PickMove(self, auto, world, targets, validity):
        allowed_moves = []
        coords = (auto.pos.x, auto.pos.y)
        repeat = coords in self.history
        
        self.history.append(coords)
        if len(self.history) > 10:
            self.history.pop(0)

        for i in range(len(targets)):
            if validity[i]:
                if not (targets[i].x == auto.pos.x and targets[i].y == auto.pos.y):
                    allowed_moves.append(targets[i])

        if len(allowed_moves) == 0:
            return auto.pos

        index = -1
        if repeat and len(allowed_moves) > 1:
            index = -2
        return allowed_moves[index]     
        
