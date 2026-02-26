import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):


    def __init__(self, track):
        super().__init__()
        self.last_move = None
        self.move_history = []

    def GetName(self) -> str:
        return "Auto"

    def PickMove(self, auto, world, targets, validity):
        if not validity or len(validity) == 0:
            return None
        move = random.choice(validity)
        self.last_move = move
        self.move_history.append(move)
        return move

    def make_decision(self):
        pass

    def get_move_history(self):
        return self.move_history.copy()

    def reset(self):
        self.last_move = None
        self.move_history = []
