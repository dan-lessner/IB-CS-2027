import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.step = 0

    def GetName(self) -> str:
        return "longTrace"

    def PickMove(self, auto, world, targets, validity):
        pass
    def targetRayCastLength(self, auto, world, target, validity):
        rayCastVector = [target[0] -auto.pos.x,auto.pos.y - target[1]]
        
        
        