import random
import math
from simulation.script_api import AutoAuto
def clamp(n,min,max):
    if n < min:
        n = min
    if n > max:
        n = max
    else: return n
class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.step = 0
        self.processedWorld = []

    def GetName(self) -> str:
        return "longTrace (DO NOT FUCKING RUN I FUKCING BEG)"

    def PickMove(self, auto, world, targets, validity):
        pass
    
    def preProcess(self,world):
        width = len(world.road)
        height = len(world.road[0])
        for _ in range(width):
           self.processedWorld.append([])
           for u in range(height):
               self.processedWorld[u].append([0,False]) 
        for x in range(width):
            #TS WRONG I NEED TO FIX
            for y in range(height):
                if world.road[x+1][y+1] == True and world.road[x+1][y-1] == True and world.road[x-1][y+1] == True and world.road[x-1][y-1] == True:
                    self.processedWorld[x][y][1] == True

    
    def targetRayCastLength(self, auto, world, target, validity):
        rayCastVector = [target[0] -auto.pos.x,auto.pos.y - target[1]]
        for _ in range(99):
            try:
                if not world.road[auto.pos.x + _ * rayCastVector[0]] [auto.pos.y + _ * rayCastVector[1]]:
                    fullVector = [auto.pos.x + _ * rayCastVector[0],auto.pos.y + _ * rayCastVector[1]]
                    break
            except:
                break
        pivot = [fullVector[0]*0.5,fullVector[1]*0.5]
        for _ in range(99):
            pass
        
        
        