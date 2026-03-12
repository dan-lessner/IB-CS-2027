import random
from simulation.script_api import AutoAuto

class Auto(AutoAuto):
    def __init__(self, track) -> None: 
        super().__init__()  
        self.step = 0
        self.bad_actions = set()
        self.last_action = None
        self.last_positions = []
        self.last_direction = None

    def GetName(self):
        return "Luci"

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None

        # track position history
        self.last_positions.append((auto.pos.x, auto.pos.y))
        if len(self.last_positions) > 5:
            self.last_positions.pop(0)

        # detect if stuck
        stuck = False
        if len(self.last_positions) == 5:
            xs = [p[0] for p in self.last_positions]
            if max(xs) - min(xs) < 2:
                stuck = True

      
        valid_moves = [targets[i] for i in range(len(targets)) if validity[i]]
        pool = valid_moves if valid_moves else list(targets)

        current_x = auto.pos.x
        current_y = auto.pos.y

       
        if stuck:
             # compute all possible directions
             dirs = [(m.x - current_x, m.y - current_y) for m in pool]

             # avoid repeating the same direction
             alternative_moves = [
            m for m in pool
             if (m.x - current_x, m.y - current_y) != self.last_direction
        ]

        if alternative_moves:
            move = random.choice(alternative_moves)
        else:
            move = random.choice(pool)

        self.last_direction = (move.x - current_x, move.y - current_y)
        return move

        self.last_direction = (move.x - current_x, move.y - current_y)
        return pool[0]
