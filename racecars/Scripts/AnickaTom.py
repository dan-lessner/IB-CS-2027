import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.last_positions = []
        self.direction = (1, 0)

    def GetName(self) -> str:
        return "Anna"

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None

        cx = auto.pos.x
        cy = auto.pos.y

        # -------------------------
        # track recent positions
        # -------------------------
        self.last_positions.append((cx, cy))
        if len(self.last_positions) > 8:
            self.last_positions.pop(0)

        # -------------------------
        # stuck detection
        # -------------------------
        stuck = False
        if len(self.last_positions) == 8:
            xs = [p[0] for p in self.last_positions]
            ys = [p[1] for p in self.last_positions]
            if (max(xs) - min(xs) < 2) and (max(ys) - min(ys) < 2):
                stuck = True

        # -------------------------
        # valid move pool
        # -------------------------
        valid_moves = []
        for i in range(len(targets)):
            if validity is None or (i < len(validity) and validity[i]):
                valid_moves.append((targets[i], i))

        pool = valid_moves if valid_moves else [(targets[i], i) for i in range(len(targets))]

        # -------------------------
        # scoring
        # -------------------------
        best_move = None
        best_score = float("-inf")

        for move, idx in pool:
            dx = move.x - cx
            dy = move.y - cy

            if dx == 0 and dy == 0:
                continue

            # normalize vectors for direction comparison
            prev_dx, prev_dy = self.direction
            prev_len = max((prev_dx**2 + prev_dy**2) ** 0.5, 0.001)
            cur_len = max((dx**2 + dy**2) ** 0.5, 0.001)

            ndx, ndy = dx / cur_len, dy / cur_len
            pdx, pdy = prev_dx / prev_len, prev_dy / prev_len

            # alignment = dot product (1 = straight, -1 = opposite)
            alignment = ndx * pdx + ndy * pdy

            if stuck:
                score = abs(dx) + abs(dy) + random.uniform(0, 2)

            else:
                # strong reward for going forward
                forward_score = dx * 4

                # penalize vertical drift
                vertical_penalty = abs(dy) * 1.2

                # penalize turning (low alignment)
                turn_penalty = (1 - alignment) * 3

                # tiny diagonal bonus (just to help corners)
                diagonal_bonus = 0.5 if abs(dx) > 0 and abs(dy) > 0 else 0

                score = forward_score - vertical_penalty - turn_penalty + diagonal_bonus

                # slight randomness so ties don't lock
                score += random.uniform(0, 0.1)

            if score > best_score:
                best_score = score
                best_move = move
                self.direction = (dx, dy)

        if best_move is None:
            return targets[0]

        return best_move