from simulation.script_api import AutoAuto, WorldState
import random

class Auto(AutoAuto):
    def __init__(self, track):
        super().__init__()
        self.direction = [1, 0]

    def GetName(self) -> str:
        return "Škoda"
    
    def PickMove(self, auto, world, targets, validity):
        current_pos = (int(auto.pos.x), int(auto.pos.y))

        for i in range(len(targets)):
            if targets[i].x == auto.pos.x + self.direction[0] and targets[i].y == auto.pos.y + self.direction[1]:
                if validity[i]:
                    return targets[i]
                else:
                    if self.direction[0] == 0:
                        self.direction = [1, 0]
                    else:
                        self.direction = [0, random.choice([-1, 1])]
                    return auto.pos
                    
        