import random
import math
from simulation.script_api import AutoAuto
def activeClamp(n,diff,min,max):
    if n + diff < min:
        return min
    if n + diff > max:
        return max
    else: return n + diff
class Auto(AutoAuto):
    def __init__(self,track) -> None:
        super().__init__()
        self.step = 0
        self.road_mask = track.road_mask
        self.width = len(track.road_mask)
        self.height = len(track.road_mask[0])
        

    def GetName(self) -> str:
        return "longTrace (DO NOT FUCKING RUN I FUCKING BEG)"

    def PickMove(self, auto, world, targets, validity):
        pass
    
    def targetRayCastLength(self, auto, target):
        rayCastVector = [target[0] -auto.pos.x,auto.pos.y - target[1]]
        for i in range(max(self.width,self.height)):
                if self.road_mask[auto.pos.x + i * rayCastVector[0]][auto.pos.y + i * rayCastVector[1]] == False:
                    fullVector = [auto.pos.x + i * rayCastVector[0],auto.pos.y + i * rayCastVector[1]]
                    carVector = [i * rayCastVector[0], i * rayCastVector[1]]
                    carVectorConst = carVector[1]/carVector[0]
                    xi = activeClamp(fullVector[0], 0 , 0 , self.width)
                    yi = activeClamp(fullVector[1], 0 , 0 , self.width)
                    if xi != auto.pos.x + i * rayCastVector[0]:
                        fy = (carVector[1]/carVectorConst) + auto.pos.y
                        fCoord = [xi, fy]
                    elif yi != auto.pos.y + i * rayCastVector[0]:
                        fx = (carVector[0] * carVectorConst) + auto.pos.x
                        fCoord = [fx, yi]
                    finVector = [fCoord[0] - auto.pos.x, fCoord[1] - auto.pos.y]
                    rayCastLength = math.sqrt(pow(finVector[0],2) + pow(finVector[1],2) )
                    return rayCastLength
                    
                    
                    
                
                
            

        
        
