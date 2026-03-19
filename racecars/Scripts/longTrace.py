import random
import math
from simulation.script_api import AutoAuto
from simulation.game_state import Vector2i
fCoord =[]

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
        return "longTrace (I fucking hate this thing)"

    def PickMove(self, auto, world, targets, validity):
        largest = Vector2i(0,0)
        for i in range(min(len(validity), len(targets))):
            if validity[i]:
                if self.targetRayCastLength(auto,targets[i]) > math.sqrt(pow(largest.x,2) + pow(largest.y,2) ):
                    largest = targets[i]
        print("largest: " + str(largest.x)+" "+str(largest.y))
        # return largest
    
    def targetRayCastLength(self, auto, target):
        print('target: ' + str(target))
        global fCoord
        fCoord =[]
        rayCastVector = [target.x - auto.pos.x , target.y - auto.pos.y]
        print('rayCastVector: ' + str(rayCastVector))
        for i in range(max(self.width,self.height)):
                if self.road_mask[auto.pos.x + i * rayCastVector[0]][auto.pos.y + i * rayCastVector[1]] == False:
                    
                    fullVector = [auto.pos.x + i * rayCastVector[0],auto.pos.y + i * rayCastVector[1]]
                    print("fullVector: " + str(fullVector))
                    carVector = [i * rayCastVector[0], i * rayCastVector[1]]
                    print("carVector: " + str(carVector))
                    if carVector[0] != 0:
                        carVectorConst = carVector[1]/carVector[0]
                    else:
                        carVectorConst = math.inf
                    print("carVectorConst: " + str(carVectorConst))

                    xi = activeClamp(fullVector[0], 0 , 0 , self.width)
                    yi = activeClamp(fullVector[1], 0 , 0 , self.width)
                    print("xi: "+ str(xi) + " yi: "+ str(yi))
                    fCoord =[]
                    if xi != auto.pos.x + i * rayCastVector[0]:
                        fy = (carVector[1]/carVectorConst) + auto.pos.y
                        fCoord = [xi, fy]
                    elif yi != auto.pos.y + i * rayCastVector[0]:
                        fx = (carVector[0] * carVectorConst) + auto.pos.x
                        fCoord = [fx, yi]
                    else:
                        fCoord = [xi,yi]
                    
                    
                    if carVectorConst == math.inf:
                        fCoord[0] = auto.pos.x
                    
                    #is this needed???
                    if rayCastVector[0] == 0 and rayCastVector[1] ==0:
                        return 0
                          
                    print('fCoord: ' + str(fCoord))
                    finVector = [fCoord[0] - auto.pos.x, fCoord[1] - auto.pos.y]
                    rayCastLength = math.sqrt(pow(finVector[0],2) + pow(finVector[1],2) )
                    
                    print("x: " + str(target.x) + " y: " + str(target.y) + " Length: " + str(rayCastLength))
                    return rayCastLength
                
        return 0
                    
                    
                    
                
                
            

        
        
