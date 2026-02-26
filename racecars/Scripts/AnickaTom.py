import random
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()

        # direction vector (dx, dy)
        self.direction = (1, 0)   # start moving right

        # remember last positions to detect loops
        self.last_positions = []
        self.stuck_counter = 0

    def GetName(self) -> str:
        return "AnickaTom"

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None

        cx = auto.pos.x
        cy = auto.pos.y

        # -------------------------
        # MEMORY (for stuck detect)
        # -------------------------
        self.last_positions.append((cx, cy))
        if len(self.last_positions) > 8:
            self.last_positions.pop(0)

        stuck = False
        if len(self.last_positions) == 8:
            xs = [p[0] for p in self.last_positions]
            ys = [p[1] for p in self.last_positions]

            if max(xs) - min(xs) < 2 and max(ys) - min(ys) < 2:
                stuck = True

        if stuck:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0

        # -------------------------
        # VALID MOVE POOL
        # -------------------------
        valid_moves = []
        for i in range(len(targets)):
            if validity is None or (i < len(validity) and validity[i]):
                valid_moves.append(targets[i])

        pool = valid_moves if valid_moves else targets

        # -------------------------
        # 🚨 HARD ESCAPE
        # -------------------------
        if self.stuck_counter > 2:
            # pick farthest move to break loop
            best = max(pool, key=lambda m: abs(m.x - cx) + abs(m.y - cy))
            self.direction = (best.x - cx, best.y - cy)
            return best

        # -------------------------
        # NORMAL AUTONOMOUS DRIVE
        # -------------------------
        dx, dy = self.direction

        # try to keep moving same direction
        for m in pool:
            if (m.x - cx, m.y - cy) == (dx, dy):
                return m

        # try slight vertical adjustment (smooth steering)
        for m in pool:
            mx = m.x - cx
            my = m.y - cy

            # same forward x but different y
            if mx == dx and abs(my) <= 1:
                self.direction = (mx, my)
                return m

        # forward blocked → try vertical only (bounce up/down)
        for m in pool:
            mx = m.x - cx
            my = m.y - cy

            if mx == 0 and abs(my) == 1:
                self.direction = (mx, my)
                return m

        # fully blocked → flip vertical direction
        self.direction = (dx, -dy if dy != 0 else random.choice([-1, 1]))

        for m in pool:
            if (m.x - cx, m.y - cy) == self.direction:
                return m

        # last fallback: go furthest away
        best = max(pool, key=lambda m: abs(m.x - cx) + abs(m.y - cy))
        self.direction = (best.x - cx, best.y - cy)
        return best
