import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.last_positions = []
        self.direction = (1, 0)  # preferred movement direction

    def GetName(self) -> str:
        return "Anna"

    def PickMove(self, auto, world, targets, validity):
        # no possible moves
        if not targets:
            return None

        current_x = auto.pos.x
        current_y = auto.pos.y


        # TRACK LAST POSITIONS

        self.last_positions.append((current_x, current_y))
        if len(self.last_positions) > 8:
            self.last_positions.pop(0)


        # STUCK DETECTION

        stuck = False
        if len(self.last_positions) == 8:
            xs = [p[0] for p in self.last_positions]
            ys = [p[1] for p in self.last_positions]

            # very small movement window → stuck
            if (max(xs) - min(xs) < 2) and (max(ys) - min(ys) < 2):
                stuck = True


        # BUILD MOVE POOL

        valid_moves = []
        for i in range(len(targets)):
            if validity is None or (i < len(validity) and validity[i]):
                valid_moves.append((targets[i], i))

        # if nothing valid, allow everything as fallback
        pool = valid_moves if valid_moves else [(targets[i], i) for i in range(len(targets))]


        # CHECK FORWARD BLOCK
        
        forward_blocked = True
        for move, i in valid_moves:
            if move.x > current_x:
                forward_blocked = False
                break


        # SCORE MOVES
       
        best_move = None
        best_score = float("-inf")

        for move, idx in pool:
            dx = move.x - current_x
            dy = move.y - current_y

            # avoid zero movement unless absolutely necessary
            if dx == 0 and dy == 0:
                continue

            if stuck:
                # escape mode → choose any strong movement
                score = abs(dx) + abs(dy) + random.uniform(0, 2)

            else:
                # prefer continuing same direction
                momentum_bonus = 3 if (dx, dy) == self.direction else 0

                # diagonal movement bonus (helps cornering)
                diagonal_bonus = 1.5 if abs(dx) > 0 and abs(dy) > 0 else 0

                if forward_blocked:
                    # when blocked, prioritize turning (vertical motion)
                    score = abs(dx) + abs(dy) * 2
                else:
                    # prefer moving forward strongly
                    score = (dx * 4) - (abs(dy) * 0.5)

                score += momentum_bonus + diagonal_bonus
                score += random.uniform(0, 0.2)

            if score > best_score:
                best_score = score
                best_move = move
                self.direction = (dx, dy)

        # safety fallback
        if best_move is None:
            return targets[0]

        return best_move

