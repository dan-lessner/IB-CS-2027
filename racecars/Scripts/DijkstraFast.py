from simulation.script_api import AutoAuto, WorldState
import heapq
import math


class Auto(AutoAuto):
    def __init__(self, track):
        super().__init__()
        self.dist_to_finish = None

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

    def compute_distance_map(self, world: WorldState) -> dict:
        finish_set = {(v.x, v.y) for v in world.finish_vertices}
        
        heap = []
        dist = {}
        
        for fx, fy in finish_set:
            heap.append((0, fx, fy))
            dist[(fx, fy)] = 0
        
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        while heap:
            d, x, y = heapq.heappop(heap)
            
            if d > dist.get((x, y), float('inf')):
                continue
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                if not self.can_move(world, nx, ny, -dx, -dy):
                    continue
                
                step_dist = 1.414 if (dx != 0 and dy != 0) else 1.0
                new_dist = d + step_dist
                
                if new_dist < dist.get((nx, ny), float('inf')):
                    dist[(nx, ny)] = new_dist
                    heapq.heappush(heap, (new_dist, nx, ny))
        
        return dist

    def PickMove(self, auto, world, targets, validity):
        current = (int(auto.pos.x), int(auto.pos.y))
        
        if self.dist_to_finish is None:
            self.dist_to_finish = self.compute_distance_map(world)
        
        valid_moves = []
        for i, is_valid in enumerate(validity):
            if is_valid:
                valid_moves.append(targets[i])
        
        if len(valid_moves) == 0:
            print(f"[DijkstraFast] Warning: no valid moves at {current}, picking first target")
            return targets[0]
        
        finish_set = {(v.x, v.y) for v in world.finish_vertices}
        best_move = None
        best_dist = float('inf')
        
        for move in valid_moves:
            pos = (move.x, move.y)
            
            if pos in finish_set:
                return move
            
            dist = self.dist_to_finish.get(pos, float('inf'))
            
            if dist < best_dist:
                best_dist = dist
                best_move = move
        
        if best_move is not None:
            return best_move
        
        print(f"[DijkstraFast] Warning: no move with known distance at {current}, using Euclidean fallback")
        
        for move in valid_moves:
            min_euclidean = float('inf')
            for fv in world.finish_vertices:
                dx = move.x - fv.x
                dy = move.y - fv.y
                euclidean = math.sqrt(dx*dx + dy*dy)
                if euclidean < min_euclidean:
                    min_euclidean = euclidean
            
            if min_euclidean < best_dist:
                best_dist = min_euclidean
                best_move = move
        
        return best_move if best_move else valid_moves[0]
