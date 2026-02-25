from simulation.script_api import AutoAuto 
class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.step = 0

    def GetName(self) -> str:
        return "Lightning McQueen StepBot"

def PickMove(self, auto, world, targets, validity):
        self.step += 1
        print("krok ", self.step)

        if not targets:
        return None

        best = targets[0]
        for move in targets:
            if move.x > best.x:
                best = move

        return best