# Cutie_killer
import random
from simulation.script_api import AutoAuto, WorldState


class Auto(AutoAuto):
    def __init__(self, track) -> None: # runs at teh start, creates memory
        super().__init__()
        self.step = 0
        self.last_positions = [] # remembers the last 6 positions, defiend below
        self.stuck_counter = 0

    def GetName(self) -> str:
        return "Cutie_killer"

    def PickMove(self, auto, world, targets, validity): # runns every time
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
            # this takes the last 6 positions from the list, and if both are less than 2, it means that it is tuck in 2X2 area
            xs = [p[0] for p in self.last_positions]
            ys = [p[1] for p in self.last_positions]
            if max(xs) - min(xs) < 2 and max(ys) - min(ys) < 2:
                stuck = True

        # how many turns stuck, if unstuck then it resets to zero
        if stuck:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0 #here it resets

        # valid moves only, # i is the position in the original list, it keeps the safe options
        valid_moves = []
        for i in range(len(targets)):  # lsit of same moves 
            if validity[i]: # the move is not a wal and it goes somewehre
                if not (targets[i].x == current_x and targets[i].y == current_y):
                    valid_moves.append(targets[i])

        if len(valid_moves) == 0: # if there is no good place to go return, thanks to this it downt freeze
            return targets[-1]

        # escape when stuck, aaah
        if stuck and self.stuck_counter > 2: # if it is stuck for more than 2 turn in a row
            return valid_moves[random.randint(-2, -1)] # if stuck it chooses random, either index -2 (second to last) or -1(last)

        # finish line y position is the goal
        finish_y = current_y  # 
        if world.finish_vertices:
            finish_y = world.finish_vertices[len(world.finish_vertices) // 2].y
            # // integer division, it divides and gets rid of th edecimal, this creates the best target in the finnish line (finnish is a vertical line - middle is optimal)

        # score every move: it prioritizes going forward,  you want to be close to the y finnish line
        best_move = None
        best_score = float("-inf")

        for move in valid_moves:
            # how far is this, the multiplying by 10, gives it the importance (it can actually be any number)
            forward = move.x * 10

            # how close is this move to the finish line y
            y_closeness = -abs(move.y - finish_y)
            # abs always make the number positive
            # but by this, the closer i am the smaller number, and the system preffers high score (via moves above), so the § flips it so the closer always wins
            # here it is, that closet to zero winssss

            score = forward + y_closeness
            # total score is  the sum between forward progress and finnish line allignment

            if score > best_score:

                best_score = score
                best_move = move

        return best_move # gives the best of the best, simply the best move
    



    # how it work: finds where it is --store memory/ moves ---if its stuck it deals with it on random -- wehr is the finnish line (i am for the middle)--i want to go forward, but being close the y line is niceee--- moves according to the highest score