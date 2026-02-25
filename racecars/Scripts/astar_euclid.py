from simulation.game_state import Vector2i, Vertex
from simulation.script_api import AutoAuto, WorldState

class Node:
    def __init__(self, pos: Vector2i, g, h, f, parent):
        self.pos = pos
        self.g = g
        self.h = h
        self.f = f
        self.parent = parent
    
    def __str__(self):
        return f"Node(pos={self.pos}, g={self.g}, h={self.h}, f={self.f})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if isinstance(other, Vector2i):
            return self.pos == other
        return self.pos == other.pos
    

class Auto(AutoAuto):


    def GetName(self) -> str:
        return "A* euclid"
    
    def __init__(self):
        super().__init__()
        self.path = None
    
    def _diagonal_dist(self,start: Vector2i, end: Vector2i):
        return max(abs(start.x-end.x),abs(start.y-end.y))
    
    def _euclidean_dist(self,start: Vector2i, end: Vector2i):
        return ((start.x-end.x)**2 + (start.y-end.y)**2)**0.5
    
    def _manhattan_dist(self,start: Vector2i, end: Vector2i):
        return abs(start.x-end.x) + abs(start.y-end.y)
    
    def closest_finish(self,node: Vector2i, world: WorldState):
        finish = world.finish_vertices
        min_dist = self._euclidean_dist(node, finish[0])
        for i in range(1,len(finish)):
            if self._euclidean_dist(node, finish[i]) < min_dist:
                min_dist = self._euclidean_dist(node, finish[i])
        return min_dist
    
    def reconstruct_path(self,node: Node):
        path = []
        while node.parent:
            path.append(node)
            node = node.parent
        return path

    def can_move(self, world: WorldState, pos: Vector2i, new_pos: Vector2i) -> bool:
        dx = new_pos.x - pos.x
        dy = new_pos.y - pos.y
        x = pos.x
        y = pos.y
        if dx != 0 and dy != 0:
            cell_x = x if dx > 0 else x - 1
            cell_y = y if dy > 0 else y - 1
            if not world.road[cell_x][cell_y]:
                return False
        elif dx != 0:
            cell_x = x if dx > 0 else x - 1
            return not(not world.road[cell_x][y] and not world.road[cell_x][y - 1])
        else:
            cell_y = y if dy > 0 else y - 1
            return not(not world.road[x][cell_y] and not world.road[x - 1][cell_y])
        return True

    def a_star(self,start: Node, world: WorldState):
        world_len = len(world.road)
        world_height = len(world.road[0])
        open = [start]
        finish = world.finish_vertices
        closed = []
        while len(open) > 0:
            min_node = open[0]
            for o in open:
                if o.f < min_node.f:
                    min_node = o
            open.remove(min_node)
            closed.append(min_node)

            #neighbors
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    if dx == 0 and dy == 0:
                        continue
                    new_x = min_node.pos.x + dx
                    new_y = min_node.pos.y + dy
                    if Vector2i(new_x, new_y) in finish:
                        return self.reconstruct_path(Node(Vector2i(new_x, new_y), 0, 0, 0, min_node))
                    #out of bounds
                    if (new_x < 0 or new_x >= world_len
                        or new_y < 0 or new_y >= world_height):
                        continue
                    #not road
                    if not world.road[new_x][new_y] or not self.can_move(world, min_node.pos, Vector2i(new_x, new_y)):
                        continue
                    if Vector2i(new_x, new_y) in closed:
                        continue
                    g = min_node.g + 1
                    h = self.closest_finish(Vector2i(new_x,new_y),world)
                    f = g + h
                    if Vector2i(new_x, new_y) in open:
                        if g < open[open.index(Vector2i(new_x, new_y))].g:
                            open[open.index(Vector2i(new_x, new_y))].g = g
                            open[open.index(Vector2i(new_x, new_y))].f = f
                            open[open.index(Vector2i(new_x, new_y))].parent = min_node
                    else:
                        open.append(Node(Vector2i(new_x,new_y), g, h, f, min_node))
    
    def PickMove(self, auto, world, targets, validity):
        if not self.path:
            start_node = Node(auto.pos, 0, self.closest_finish(auto.pos,world), self.closest_finish(auto.pos,world),None)
            self.path = self.a_star(start_node, world)
        next_pos = self.path.pop().pos
        return Vertex(next_pos.x, next_pos.y)