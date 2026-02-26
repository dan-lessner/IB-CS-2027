import random
from simulation.script_api import AutoAuto, WorldState

class Auto(AutoAuto):
    def _init_(self) -> None:
        super()._init_()
        self.step = 0
        self.bad_actions = set()
        self.last_action = None
        self.best_targets = []


    def PickMove(self,auto,world, targets, validity):
        if not targets:
            return None
        for move in targets:
            dx = move[0] - world.car_x
            dy = move[1] - world.car_y
            if dx > 0:
                steering = 1
            elif dx < 0:
                steering = -1
            else:
                steering = 0
            if dy > 0:
                throttle = 1
            elif dy < 0:
                throttle = -1
            else:
                throttle = 0
            return (targets)

    def GetName(self):
        return "Luci"

    def step(self, car_state):

        self.last_positions.append((car_state.pos.x, car_state.pos.y))  # append adds to the end of the list
        if len(self.last_positions) > 5: # how many in the list, saves
            self.last_positions.pop(0) # removes the oldest item
            
        stuck = False
        if len(self.last_positions) == 5:
            xs = [p[0] for p in self.last_positions]
            if max(xs) - min(xs) < 2:  # if the car hasnt moved more than 2 blocks horizontaly, its stuck
                # it only cares about moving forward, x,
                stuck = True

        # if the car crashed, remember the last action as bad
        if car_state.collided and self.last_action is not None:
            self.bad_actions.add(self.last_action)
        
        # try random action until we find one not marked as bad
        while True:
            steering = random.uniform(-1, 1)
            throttle = random.uniform(0, 1)
            action = (round(steering, 1), round(throttle, 1))
            if action not in self.bad_actions:
                self.last_action = action  # save action for next frame
                return steering, throttle