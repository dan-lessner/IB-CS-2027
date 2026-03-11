from simulation.script_api import AutoAuto


class Auto(AutoAuto):

    def __init__(self, track):
        super().__init__()
        self.direction = (1, 0)

    def GetName(self) -> str:
        return "AnickaTom"

    def PickMove(self, auto, world, targets, validity):

        if not targets:
            return None

        current_x = auto.pos.x
        current_y = auto.pos.y

        best_move = None
        best_score = float("-inf")

        for i, move in enumerate(targets):

            if validity and not validity[i]:
                continue

            dx = move.x - current_x
            dy = move.y - current_y

            # jedeme co nejvíc doprava, cause women are always right
            score = dx * 10

            # zadny klikateni jinak minus body debile
            score -= abs(dy) * 2

            # bodik navic (kein schwarzpuntik) kdyz jedes dobre
            if (dx, dy) == self.direction:
                score += 5

            # divna zmena smeru = problem
            score -= abs(dy - self.direction[1]) * 2

            if score > best_score:
                best_score = score
                best_move = move
                self.direction = (dx, dy)

        if best_move is None:
            return targets[0]

        return best_move
