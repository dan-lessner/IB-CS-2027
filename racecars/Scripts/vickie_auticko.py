# Viki car
import random
from simulation.script_api import AutoAuto, WorldState


class Auto(AutoAuto):
    def __init__(self) -> None:
        super().__init__()
        self.step = 0
        self.last_positions = []
        self.direction = (1, 0)  # tracks current facing direction (x, y)

    def GetName(self) -> str:
        return "Cutie"

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None
        # it saves the position, so we can compare
        current_x = auto.pos.x
        current_y = auto.pos.y

        # track recent positions
        self.last_positions.append((current_x, current_y))  # append adds to the end of the list
        if len(self.last_positions) > 8: # how many in the list, saves only 8
            self.last_positions.pop(0) # removes the oldest item

        # detect stuck
        stuck = False
        if len(self.last_positions) == 8:
            xs = [p[0] for p in self.last_positions]
            if max(xs) - min(xs) < 2:  # if the car hasnt moved more than 2 blocks horizontaly, its stuck
                # it only cares about moving forward, x, 
                stuck = True

        # separate valid and invalid moves
        valid_moves = [(targets[i], i) for i in range(len(targets)) if validity[i]]
        pool = valid_moves if valid_moves else [(targets[i], i) for i in range(len(targets))]

        # check if forward is blocked
        forward_blocked = not any(m.x > current_x for m, i in valid_moves)
        # if none have bigger x than currect position, then forward is blocked


        best_move = None
        best_score = float("-inf")  # negative infinitive, so the first move will always be better

        #loop
        for move, idx in pool:
            dx = move.x - current_x  # forward, + right, - left
            dy = move.y - current_y  # verticall, + down, - up

            if stuck:
                score = abs(dx) + abs(dy) + random.uniform(0, 1.0) # if stuck it chooses any random direction 


            else:
                

                # if it goes in the same direction, give 3 point
                momentum_bonus = 0
                if (dx, dy) == self.direction:
                    momentum_bonus = 3  

                # if it goes horizontally and vertically, then give bonus (vertical crosees more)
                diagonal_bonus = 0
                if abs(dx) > 0 and abs(dy) > 0:
                    diagonal_bonus = 1.5

                # if cutie is in a corner
                if forward_blocked:
                    score = abs(dx) + abs(dy) * 2 # 2 x going up/down
                else:
                    score = (dx * 4) - abs(dy) * 0.5  # 4 for going forward , and penaly for turning
                
                # it helps it not getting stuck idk how
                score += momentum_bonus + diagonal_bonus # adds bonuus on top 
                score += random.uniform(0, 0.2)  # adds a random number, it helps it choose hen two moves score the same point (it would then pick up the first one)

            if score > best_score:  # is it the best move?
                best_score = score # new best score
                best_move = move # this move will be done
                # update direction memory
                self.direction = (dx, dy)

        return best_move