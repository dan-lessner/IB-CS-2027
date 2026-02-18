from simulation.script_api import AutoAuto, WorldState
import heapq


class Auto(AutoAuto):
    def __init__(self):
        super().__init__()
        self.path = None

    def GetName(self) -> str:
        return "DijkstraFast"

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
        
        raise RuntimeError("No path to finish found!")

    def get_dir(self, p1, p2):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dx = 0 if dx == 0 else (1 if dx > 0 else -1)
        dy = 0 if dy == 0 else (1 if dy > 0 else -1)
        return (dx, dy)

    def straight_len(self, path, start_index):
        if start_index >= len(path) - 1:
            return 0
        
        direction = self.get_dir(path[start_index], path[start_index + 1])
        length = 1
        
        for i in range(start_index + 1, len(path) - 1):
            next_dir = self.get_dir(path[i], path[i + 1])
            if next_dir == direction:
                length += 1
            else:
                break
        
        return length

    def stop_dist(self, speed):
        return speed * (speed + 1) // 2

    def PickMove(self, auto, world, targets, validity):
        current = (int(auto.pos.x), int(auto.pos.y))
        vx, vy = int(auto.vel.vx), int(auto.vel.vy)
        current_speed = max(abs(vx), abs(vy))
        
        if self.path is None:
            self.path = self.computepath(current[0], current[1], world)
        
        current_index = self.path.index(current)
        remaining = len(self.path) - 1 - current_index
        
        if remaining == 0:
            valid_indices = []
            i = 0
            while i < len(validity):
                if validity[i]:
                    valid_indices.append(i)
                i += 1

            if len(valid_indices) == 0:
                return None

            return targets[valid_indices[0]]
        
        next_pos = self.path[current_index + 1]
        path_dir = self.get_dir(current, next_pos)
        
        straight_length = self.straight_len(self.path, current_index)
        
        vel_dir = (0 if vx == 0 else (1 if vx > 0 else -1),
                   0 if vy == 0 else (1 if vy > 0 else -1))
        
        if current_speed > 0 and vel_dir != path_dir:
            target_speed = current_speed - 1
        else:
            max_safe_speed = 1
            for s in range(1, 20):
                if self.stop_dist(s) <= straight_length:
                    max_safe_speed = s
                else:
                    break
            
            if current_speed < max_safe_speed:
                target_speed = current_speed + 1
            elif current_speed > max_safe_speed:
                target_speed = current_speed - 1
            else:
                target_speed = current_speed
        
        target_vx = path_dir[0] * target_speed
        target_vy = path_dir[1] * target_speed
        target_x = current[0] + target_vx
        target_y = current[1] + target_vy
        
        valid_indices = []
        i = 0
        while i < len(validity):
            if validity[i]:
                valid_indices.append(i)
            i += 1

        if len(valid_indices) == 0:
            return None

        best_mv = None
        best_dist_sq = None
        for i in valid_indices:
            mv = targets[i]
            if mv.x == target_x and mv.y == target_y:
                return mv
            dx = mv.x - target_x
            dy = mv.y - target_y
            dist_sq = dx * dx + dy * dy
            if best_dist_sq is None or dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best_mv = mv

        # Fallback: return the closest valid move (or None if none)
        return best_mv
