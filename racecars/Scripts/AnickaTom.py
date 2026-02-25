import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.last_positions = []
        self.direction = (1, 0)  # current preferred direction

    def GetName(self) -> str:
        return "Anna"

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None

        current_x = auto.pos.x
        current_y = auto.pos.y

        # =========================
        # TRACK POSITION HISTORY
        # =========================
        self.last_positions.append((current_x, current_y))
        if len(self.last_positions) > 8:
            self.last_positions.pop(0)

        # =========================
        # DETECT STUCK
        # =========================
        stuck = False
        if len(self.last_positions) == 8:
            xs = [p[0] for p in self.last_positions]
            ys = [p[1] for p in self.last_positions]

            # if we barely moved in BOTH directions → stuck
            if (max(xs) - min(xs) < 2) and (max(ys) - min(ys) < 2):
                stuck = True

        # =========================
        # BUILD MOVE POOL
        # =========================
        valid_moves = []
        for i in range(len(targets)):
            if validity is None or (i < len(validity) and validity[i]):
                valid_moves.append((targets[i], i))

        pool = valid_moves if valid_moves else [(targets[i], i) for i in range(len(targets))]

        # =========================
        # CHECK IF FORWARD BLOCKED
        # =========================
        forward_blocked = True
        for m, i in valid_moves:
            if m.x > current_x:
                forward_blocked = False
                break

        # =========================
        # SCORE MOVES
        # =========================
        best_move = None
        best_score = float("-inf")

        for move, idx in pool:
            dx = move.x - current_x
            dy = move.y - current_y

            # --- if stuck → explore randomly ---
            if stuck:
                score = abs(dx) + abs(dy) + random.uniform(0, 2)

            else:
                # prefer continuing same direction
                momentum_bonus = 0
                if (dx, dy) == self.direction:
                    momentum_bonus = 3

                # small bonus for diagonal (helps cornering)
                diagonal_bonus = 1.5 if abs(dx) > 0 and abs(dy) > 0 else 0

                # main movement scoring
                if forward_blocked:
                    # prioritize escaping vertically if blocked
                    score = abs(dx) + abs(dy) * 2
                else:
                    # strongly prefer forward movement
                    score = (dx * 4) - abs(dy) * 0.5

                # combine bonuses
                score += momentum_bonus + diagonal_bonus
                score += random.uniform(0, 0.2)

            if score > best_score:
                best_score = score
                best_move = move
                self.direction = (dx, dy)

        return best_move