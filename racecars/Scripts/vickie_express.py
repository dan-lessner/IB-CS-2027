# Express
import random
from simulation.script_api import AutoAuto, WorldState


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.step = 0  # counts steps
        self.vertical_direction = 1   # -1 is up , 1 is down
        self.last_positions = []  # remembers the last 6 positions, defiend below
        self.stuck_counter = 0

    def GetName(self) -> str:
        return "Express"

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None

        current_x = auto.pos.x
        current_y = auto.pos.y

        self.last_positions.append((current_x, current_y))
        if len(self.last_positions) > 6:
            self.last_positions.pop(0)
            #adds the current position to the memory list, it tracks where it was stuck and where not


        # detect stuck
        stuck = False
        if len(self.last_positions) == 6:
            # this takes the last 6 positions from the list, and if both are less than 2, it means that it is tuck in 1X1 area
            xs = [p[0] for p in self.last_positions]
            ys = [p[1] for p in self.last_positions]
            if max(xs) - min(xs) < 2 and max(ys) - min(ys) < 2:
                stuck = True

            # how many turns stuck, if unstuck then it resets to zero
        if stuck:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0


         # i is the position in the original list, it keeps the safe options
        valid_moves = [(targets[i], i) for i in range(len(targets)) if validity[i]]

        # what it will actually choose from 
        pool = valid_moves if valid_moves else [(targets[i], i) for i in range(len(targets))]



        # if stuck for  more than 2 turns, change the direct (1, -1)
        #  goes furthest from current position
        if stuck and self.stuck_counter > 2:
            self.vertical_direction *= -1
            best = max(pool, key=lambda mi: abs(mi[0].x - current_x) + abs(mi[0].y - current_y))
            return best[0]

        # forward and vertical, if it can, it follows this
        for move, idx in pool:
            dx = move.x - current_x
            dy = move.y - current_y
            if dx == 1 and dy == self.vertical_direction:
                return move

        # if it cannot move forward, it checks if it can just move vertically(up, down)
        for move, idx in pool:
            dx = move.x - current_x
            dy = move.y - current_y
            if dx == 0 and dy == self.vertical_direction:
                return move

        # oh no wall, bouncing of the wall, since it cannot move  froward/vertically, it  changes direction (1, -1)
        self.vertical_direction *= -1
        for move, idx in pool:
            dy = move.y - current_y
            if dy == self.vertical_direction:
                return move

        # cannot go vertically, just move front
        for move, idx in pool:
            if move.x > current_x:
                return move

        # lost option, not getting stuck, it chooses the furtherst direction, goeas anywhere
        best = max(pool, key=lambda mi: abs(mi[0].x - current_x) + abs(mi[0].y - current_y))
        return best[0]
        # max finds the biggest number
        # mi - how far horizontally/vertically it is
        # abds makes the number postive 
        # it calucates the total distance, so that is why it its +
            # look at every avaiable move, calculate how far it is, pick it and go



# IT STILL GETS STUCK WHYYYYYYYYYYYYYYYYYYYYY