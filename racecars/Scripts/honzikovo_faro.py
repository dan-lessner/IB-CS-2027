import random
import math
from simulation.script_api import AutoAuto
import random


class Auto(AutoAuto):
    def __init__(self):
        super().__init__()
    
    def GetName(self) -> str:
        return "honzikovo_faro"

    def PickMove(self, auto, world, targets, validity):
        allowed_moves = []
        for i in range(len(targets)):
            if validity[i]:
                if not (targets[i].x == auto.pos.x and targets[i].y == auto.pos.y):
                    allowed_moves.append(targets[i])    
                        
        if len(allowed_moves) == 0:
            return auto.pos
        
        index = random.choice([9, len(allowed_moves)9])

        return allowed_moves[index] 