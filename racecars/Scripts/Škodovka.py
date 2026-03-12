from simulation.script_api import AutoAuto, WorldState
import random

class Auto(AutoAuto):
    def __init__(self, track):
        super().__init__()
        self.direction = [1, 0]

    def GetName(self) -> str:
        return "Škoda vyhrávat"
    
    def PickMove(self, auto, world, targets, validity):
        possible_moves = []                    

        for i in range(len(targets)):
            possible_moves.append([targets[i].x, targets[i].y])
        
        print(possible_moves)

        if self.direction[0] == 0:
            if validity[possible_moves.index([auto.pos.x+1, auto.pos.y + self.direction[1]])]:
                self.direction[0] = 1

        if not validity[possible_moves.index([auto.pos.x + self.direction[0], auto.pos.y + self.direction[1]])]:
            if self.direction[0] == 1:
                if validity[possible_moves.index([auto.pos.x + 1, auto.pos.y])]:
                    self.direction[1] = 0
                else:
                    self.direction[0] = 0
                    if self.direction[1] == 0:
                        self.direction[1] = random.choice([-1, 1])
                    return auto.pos
            else:
                if self.direction[1] == 0:
                    self.direction[1] == random.choice([-1, 1])
                self.direction[1] = -self.direction[1]
                return auto.pos
            
        return targets[possible_moves.index([auto.pos.x + self.direction[0], auto.pos.y + self.direction[1]])]