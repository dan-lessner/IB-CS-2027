from simulation.script_api import AutoAuto, WorldState
import heapq


class Auto(AutoAuto):
    def __init__(self, track):
        super().__init__()
        self.path = None

    def GetName(self) -> str:
        return "Dijkstra"

    def is_road(self, world: WorldState, cx: int, cy: int) -> bool:
        width = len(world.road)
        height = len(world.road[0]) if width > 0 else 0
        if 0 <= cx < width and 0 <= cy < height:
            return world.road[cx][cy]
        return False

    def is_valid_vertex(self, world: WorldState, x: int, y: int) -> bool:
        for dx in [-1, 0]:
            for dy in [-1, 0]:
                if self.is_road(world, x + dx, y + dy):
                    return True
        return False

    def can_move(self, world: WorldState, x: int, y: int, dx: int, dy: int) -> bool:
        nx, ny = x + dx, y + dy
        
        if not self.is_valid_vertex(world, nx, ny):
            return False
        
        if dx != 0 and dy != 0:
            cell_x = x if dx > 0 else x - 1
            cell_y = y if dy > 0 else y - 1
            if not self.is_road(world, cell_x, cell_y):
                return False
        elif dx != 0:
            cell_x = x if dx > 0 else x - 1
            if not self.is_road(world, cell_x, y) and not self.is_road(world, cell_x, y - 1):
                return False
        else:
            cell_y = y if dy > 0 else y - 1
            if not self.is_road(world, x, cell_y) and not self.is_road(world, x - 1, cell_y):
                return False
        
        return True

    def computepath(self, start_x: int, start_y: int, world: WorldState) -> list:
        finish_set = {(v.x, v.y) for v in world.finish_vertices}
        
        heap = [(0, start_x, start_y)]
        dist = {(start_x, start_y): 0}
        came_from = {}
        
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        while heap:
            d, x, y = heapq.heappop(heap)
            
            if d > dist.get((x, y), float('inf')):
                continue
            
            if (x, y) in finish_set:
                path = [(x, y)]
                while (x, y) in came_from:
                    x, y = came_from[(x, y)]
                    path.append((x, y))
                path.reverse()
                return path
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                is_finish = (nx, ny) in finish_set
                if not is_finish and not self.can_move(world, x, y, dx, dy):
                    continue
                
                step_dist = 1.414 if (dx != 0 and dy != 0) else 1.0
                new_dist = d + step_dist
                
                if new_dist < dist.get((nx, ny), float('inf')):
                    dist[(nx, ny)] = new_dist
                    came_from[(nx, ny)] = (x, y)
                    heapq.heappush(heap, (new_dist, nx, ny))
        
        return []  # No path found

    def PickMove(self, auto, world, targets, validity):
        current = (int(auto.pos.x), int(auto.pos.y))
        vx, vy = int(auto.vel.x), int(auto.vel.y)
        current_speed = max(abs(vx), abs(vy))
        
        valid_moves = []
        valid_move_map = {}
        for i, is_valid in enumerate(validity):
            if is_valid:
                move = targets[i]
                valid_moves.append(move)
                valid_move_map[(move.x, move.y)] = move
        
        finish_set = {(v.x, v.y) for v in world.finish_vertices}
        for move in valid_moves:
            if (move.x, move.y) in finish_set:
                return move
        
        if current_speed > 1:
            for move in valid_moves:
                move_vx = move.x - current[0]
                move_vy = move.y - current[1]
                move_speed = max(abs(move_vx), abs(move_vy))
                if move_speed < current_speed:
                    return move
            return valid_moves[0]
        
        if self.path is None:
            self.path = self.computepath(current[0], current[1], world)
        
        try:
            current_index = self.path.index(current)
        except ValueError:
            print(f"[Dijkstra] Recomputing path: current {current} not on path")
            self.path = self.computepath(current[0], current[1], world)
            try:
                current_index = self.path.index(current)
            except ValueError:
                print(f"[Dijkstra] Warning: still not on path after recompute")
                return valid_moves[0]
        
        if current_index >= len(self.path) - 1:
            return valid_moves[0]
        
        next_pos = self.path[current_index + 1]
        
        if next_pos in valid_move_map:
            return valid_move_map[next_pos]
        
        if current_speed > 0:
            for move in valid_moves:
                move_vx = move.x - current[0]
                move_vy = move.y - current[1]
                move_speed = max(abs(move_vx), abs(move_vy))
                if move_speed < current_speed:
                    return move
        
        print(f"[Dijkstra] Recomputing path: next step {next_pos} not reachable")
        self.path = self.computepath(current[0], current[1], world)
        
        try:
            current_index = self.path.index(current)
            if current_index < len(self.path) - 1:
                next_pos = self.path[current_index + 1]
                if next_pos in valid_move_map:
                    return valid_move_map[next_pos]
        except ValueError:
            pass
        
        raise RuntimeError(f"[Dijkstra] No valid move found for current {current} with velocity ({vx}, {vy})")
