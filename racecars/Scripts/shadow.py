from simulation.script_api import AutoAuto


class Auto(AutoAuto):
    def __init__(self, track) -> None:
        super().__init__()

    def GetName(self) -> str:
        return "Shadow"

    def PickMove(self, auto, world, targets, validity):
        if not targets:
            return None

        # find the car
        target_car = None
        for car in world.cars:
            if car.name == "Fildy Driver":
                target_car = car
                break

        # mov it mo v eit 
        if target_car is None:
            for i, move in enumerate(targets):
                if validity[i] and move.x > auto.pos.x:
                    return move
            return targets[0]

        # 
        target_x = target_car.pos.x
        target_y = target_car.pos.y

        best_move = None
        best_dist = float('inf')

        for i, move in enumerate(targets):
            if validity[i]:
                dist = abs(move.x - target_x) + abs(move.y - target_y)
                if dist < best_dist:
                    best_dist = dist
                    best_move = move

        if best_move is not None:
            return best_move

        # 
        for i, move in enumerate(targets):
            if validity[i]:
                return move
        return targets[0]