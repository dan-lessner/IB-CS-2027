import math
from operator import index
import random
from shutil import move
from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self,track) -> None:
        super().__init__()
        self.step = 0
        self.y_direction = 1
        self.history = []
    
    def GetName(self) -> str:
        return "Fildycompet Driver"

    def PickMove(self, auto, world, targets, validity):
        valid_moves = []
        for i, vertex in enumerate(targets):
            if validity[i] and not (vertex.x == auto.pos.x and vertex.y == auto.pos.y):
                valid_moves.append((i, vertex))
        if not valid_moves:
            return auto.pos
        right_moves = [m for m in valid_moves if m[1].x > auto.pos.x]

        if right_moves:
            max_x = max(m[1].x for m in right_moves)
            best_right_moves = [m for m in right_moves if m[1].x == max_x]
            same_y_move = [m for m in best_right_moves if m[1].y == auto.pos.y]
            if same_y_move:
                chosen_index = same_y_move[0][0]
            else:
                chosen_index = random.choice(best_right_moves)[0]
            return targets[chosen_index]

        if self.y_direction == 1:
            vertical_moves = [m for m in valid_moves if m[1].y > auto.pos.y]
        else:
            vertical_moves = [m for m in valid_moves if m[1].y < auto.pos.y]

        if vertical_moves:
            chosen_index = random.choice(vertical_moves)[0]
        else:
            self.y_direction *= -1
            if self.y_direction == 1:
                vertical_moves = [m for m in valid_moves if m[1].y > auto.pos.y]
            else:
                vertical_moves = [m for m in valid_moves if m[1].y < auto.pos.y]
                
            if vertical_moves:
                chosen_index = random.choice(vertical_moves)[0]
            else:
                chosen_index = random.choice(valid_moves)[0]

        return targets[chosen_index]
    
