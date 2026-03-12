from simulation.script_api import AutoAuto, WorldState
from collections import deque


class Auto(AutoAuto):
    def __init__(self, track):
        super().__init__()
        self.plan = None
        self.plan_index = 0
        self.road = None
        self.finish_set = None
        self.road_width = 0
        self.road_height = 0

    def GetName(self) -> str:
        return "DijkstraOptimal"

    def is_road(self, cx: int, cy: int) -> bool:
        if cx < 0 or cx >= self.road_width:
            return False
        if cy < 0 or cy >= self.road_height:
            return False
        return self.road[cx][cy]

    def point_is_on_road(self, x: float, y: float) -> bool:
        if x < 0 or y < 0 or x > self.road_width or y > self.road_height:
            return False

        epsilon = 0.000001
        base_x = int(x)
        base_y = int(y)

        candidates_x = [base_x]
        candidates_y = [base_y]

        if abs(x - round(x)) < epsilon:
            candidates_x.append(base_x - 1)
        if abs(y - round(y)) < epsilon:
            candidates_y.append(base_y - 1)

        for cx in candidates_x:
            for cy in candidates_y:
                if self.is_road(cx, cy):
                    return True
        return False

    def vertex_inside(self, vx: int, vy: int) -> bool:
        for cx in range(vx - 1, vx + 1):
            for cy in range(vy - 1, vy + 1):
                if self.is_road(cx, cy):
                    return True
        return False

    def line_is_valid(self, x0: int, y0: int, x1: int, y1: int) -> bool:
        dx = x1 - x0
        dy = y1 - y0
        
        if dx == 0 and dy == 0:
            return self.point_is_on_road(float(x0), float(y0))
        
        if not self.vertex_inside(x1, y1):
            return False
        
        t_values = [0.0, 1.0]
        
        if dx != 0:
            if dx > 0:
                for x in range(x0 + 1, x1):
                    t = (x - x0) / dx
                    if 0 < t < 1:
                        t_values.append(t)
            else:
                for x in range(x0 - 1, x1, -1):
                    t = (x - x0) / dx
                    if 0 < t < 1:
                        t_values.append(t)
        
        if dy != 0:
            if dy > 0:
                for y in range(y0 + 1, y1):
                    t = (y - y0) / dy
                    if 0 < t < 1:
                        t_values.append(t)
            else:
                for y in range(y0 - 1, y1, -1): 
                    t = (y - y0) / dy
                    if 0 < t < 1:
                        t_values.append(t)
        
        t_values.sort()
        epsilon = 0.0000001
        
        for i in range(len(t_values) - 1):
            t0 = t_values[i]
            t1 = t_values[i + 1]
            if t1 - t0 > epsilon:
                t_mid = (t0 + t1) * 0.5
                x_mid = x0 + dx * t_mid
                y_mid = y0 + dy * t_mid
                if not self.point_is_on_road(x_mid, y_mid):
                    return False
        
        return True

    def compute_path(self, start_x: int, start_y: int, start_vx: int, start_vy: int, max_speed: int = 20) -> list:
        start_state = (start_x, start_y, start_vx, start_vy)
        
        queue = deque([start_state])
        came_from = {start_state: None}
        
        accelerations = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        
        iterations = 0
        max_iterations = 300000
        
        while queue and iterations < max_iterations:
            iterations += 1
            x, y, vx, vy = queue.popleft()
            
            if (x, y) in self.finish_set:
                path = []
                state = (x, y, vx, vy)
                while state is not None:
                    path.append(state)
                    state = came_from[state]
                path.reverse()
                return path
            
            for ax, ay in accelerations:
                new_vx = vx + ax
                new_vy = vy + ay
                
                if abs(new_vx) > max_speed or abs(new_vy) > max_speed:
                    continue
                
                new_x = x + new_vx
                new_y = y + new_vy
                
                if new_x < 0 or new_y < 0 or new_x > self.road_width or new_y > self.road_height:
                    continue
                
                new_state = (new_x, new_y, new_vx, new_vy)
                
                if new_state in came_from:
                    continue
                
                if self.line_is_valid(x, y, new_x, new_y):
                    came_from[new_state] = (x, y, vx, vy)
                    queue.append(new_state)
        
        return []

    def PickMove(self, auto, world, targets, validity):
        curr_state = (int(auto.pos.x), int(auto.pos.y), int(auto.vel.x), int(auto.vel.y))
        
        if self.road is None:
            self.road = world.road
            self.road_width = len(world.road)
            self.road_height = len(world.road[0]) if self.road_width > 0 else 0
            self.finish_set = {(v.x, v.y) for v in world.finish_vertices}
        
        valid_moves = []
        valid_move_map = {}
        for i, is_valid in enumerate(validity):
            if is_valid:
                move = targets[i]
                valid_moves.append(move)
                valid_move_map[(move.x, move.y)] = move
        
        for move in valid_moves:
            if (move.x, move.y) in self.finish_set:
                return move
        
        need_recompute = False
        if self.plan is None or len(self.plan) == 0:
            need_recompute = True
        elif self.plan[self.plan_index] != curr_state:
            found = False
            for i in range(self.plan_index, len(self.plan)):
                if self.plan[i] == curr_state:
                    self.plan_index = i
                    found = True
                    break
            if not found:
                print(f"[DijkstraOptimal] Deviated off plan - {curr_state}")
                need_recompute = True
        
        if need_recompute:
            self.plan = self.compute_path(curr_state[0], curr_state[1], curr_state[2], curr_state[3])
            self.plan_index = 0
        
        next_state = self.plan[self.plan_index + 1]
        next_x, next_y = next_state[0], next_state[1]
        # print(f"[DijkstraOptimal] Current: {curr_state}, Next: {next_state}, Valid moves: {[ (m.x, m.y) for m in valid_moves ]}")
        
        if (next_x, next_y) in valid_move_map:
            self.plan_index += 1
            return valid_move_map[(next_x, next_y)]
        
        print(f"[DijkstraOptimal] Planned move {next_state} not available, recomputing...")
        self.plan = self.compute_path(curr_state[0], curr_state[1], curr_state[2], curr_state[3])
        self.plan_index = 0
        
        if len(self.plan) > 1:
            next_state = self.plan[1]
            next_x, next_y = next_state[0], next_state[1]
            if (next_x, next_y) in valid_move_map:
                self.plan_index = 1
                return valid_move_map[(next_x, next_y)]
        
        print(f"[DijkstraOptimal] No valid path, picking first valid move")
        self.plan = None
        return valid_moves[0]