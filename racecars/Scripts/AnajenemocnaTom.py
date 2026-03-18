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

        valid_moves = []

        for i, move in enumerate(targets):
            if validity is None or validity[i]:
                valid_moves.append(move)

        if not valid_moves:
            return targets[0]

        # jedeme dopredu
        forward_possible = False
        for move in valid_moves:
            if move.x > current_x:
                forward_possible = True
                break

        best_move = None
        best_score = float("-inf")

        for move in valid_moves:

            dx = move.x - current_x
            dy = move.y - current_y

            if forward_possible:
                # prefer strong forward movement
                score = dx * 10 - abs(dy) * 2
            else:
                # if blocked, prioritize turning
                score = abs(dy) * 6 + dx

                # bonusovy bodik
            if (dx, dy) == self.direction:
                score += 4

            if score > best_score:
                best_score = score
                best_move = move
                self.direction = (dx, dy)

        return best_move
