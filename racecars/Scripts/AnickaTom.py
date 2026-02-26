import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()

        # remembers recent positions to detect loops
        self.last_positions = []

        # current preferred movement direction
        self.direction = (1, 0)

        # counts how long we are stuck
        self.stuck_counter = 0

    def GetName(self) -> str:
        return "AnickaTom"

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None

        current_x = auto.pos.x
        current_y = auto.pos.y

        
        # tracker of last posit
        
        self.last_positions.append((current_x, current_y))
        if len(self.last_positions) > 8:
            self.last_positions.pop(0)

        
        # stuck detection
        
        stuck = False
        if len(self.last_positions) == 8:
            xs = [p[0] for p in self.last_positions]
            ys = [p[1] for p in self.last_positions]

            if (max(xs) - min(xs) < 2) and (max(ys) - min(ys) < 2):
                stuck = True

        # update stuck counter
        if stuck:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0

        # build move pool
      
        valid_moves = []
        for i in range(len(targets)):
            if validity is None or (i < len(validity) and validity[i]):
                valid_moves.append((targets[i], i))

        pool = valid_moves if valid_moves else [(targets[i], i) for i in range(len(targets))]

        
        # escape solution
        
        if self.stuck_counter > 2:
            # reset direction randomly but generally forward
            self.direction = (1, random.choice([-1, 0, 1]))

            # choose the move that gets farthest away
            best = max(
                pool,
                key=lambda mi: abs(mi[0].x - current_x) + abs(mi[0].y - current_y)
            )
            return best[0]


        # avoid backtrackiung

        last_pos = self.last_positions[-2] if len(self.last_positions) >= 2 else None

        # check if forward block

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

            # skip zero move
            if dx == 0 and dy == 0:
                continue

            # avoid going directly back where we came from
            if last_pos and (move.x, move.y) == last_pos:
                continue

            if stuck:
                # escape mode (mild)
                score = abs(dx) + abs(dy) + random.uniform(0, 2)

            else:
                # prefer continuing same direction (reduced strength)
                momentum_bonus = 1.5 if (dx, dy) == self.direction else 0

                # diagonal movement bonus
                diagonal_bonus = 1 if abs(dx) > 0 and abs(dy) > 0 else 0

                if forward_blocked:
                    # prioritize turning when blocked
                    score = abs(dx) + abs(dy) * 2
                else:
                    # prefer strong forward movement
                    score = (dx * 4) - (abs(dy) * 0.5)

                score += momentum_bonus + diagonal_bonus
                score += random.uniform(0, 0.2)

            if score > best_score:
                best_score = score
                best_move = move
                self.direction = (dx, dy)


        # SAFETY FALLBACK

        if best_move is None:
            return targets[0]

        return best_move
