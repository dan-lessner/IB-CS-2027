import random
import math
from simulation.script_api import AutoAuto

class Auto(AutoAuto):

    def __init__(self) -> None:
        self.dir = (1, 0)
        super().__init__()
        self.step = 0

    def GetName(self) -> str:
        return "Lightning McQueen"

    def _get_finish_xy(self, world):
    
        candidates = [
            "finish", "finish_pos", "finishPosition", "finish_point",
            "goal", "goal_pos", "target", "target_pos"
        ]

        for name in candidates:
            if hasattr(world, name):
                f = getattr(world, name)
                # If finish is an object with x/y
                if hasattr(f, "x") and hasattr(f, "y"):
                    return (f.x, f.y)
                # If finish is a tuple/list like (x, y)
                if isinstance(f, (tuple, list)) and len(f) >= 2:
                    return (f[0], f[1])

        return None

    def PickMove(self, auto, world, targets, validity):
        self.step += 1
        print("kroky:", self.step)

        if not targets:
            return None

        finish_xy = self._get_finish_xy(world)

        if finish_xy is not None:
            best = None
            best_dist = None

            for move in targets:
                d = euclidean((move.x, move.y), finish_xy)
                if best_dist is None or d < best_dist:
                    best_dist = d
                    best = move

            return best

        best = targets[0]
        for move in targets:
            if move.x > best.x:
                best = move
        return best


def euclidean(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.sqrt(dx * dx + dy * dy)


def pick_nearest_vertex(vertices, position, visited):
    best_idx = None
    best_dist = None
    i = 0
    while i < len(vertices):
        v = vertices[i]
        if v in visited:
            i = i + 1
            continue
        d = euclidean(position, v)
        if best_dist is None or d < best_dist:
            best_dist = d
            best_idx = i
        i = i + 1
    return best_idx


def random_unit_step():
    angle = random.random() * 2.0 * math.pi
    dx = math.cos(angle)
    dy = math.sin(angle)
    return dx, dy


dx, dy = random_unit_step()