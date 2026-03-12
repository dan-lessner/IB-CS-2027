"""TightropeWalker – path-planning car controller.

Pipeline (run once on first move):
  A. BFS          – find any valid vertex-path from start to finish
  B. Tightening   – greedily skip nodes where a direct segment is valid
  C. Bresenham    – densify the tight path into per-cell waypoints

PickMove then tracks the next waypoint and picks the allowed move
that gets the car closest to it.
"""

from collections import deque

from simulation.script_api import AutoAuto
from simulation.game_state import Vertex


# ---------------------------------------------------------------------------
# Controller class
# ---------------------------------------------------------------------------

class Auto(AutoAuto):
    def __init__(self, track):
        super().__init__()
        self.track = track
        self.waypoints = None   # computed lazily on the first move

    def GetName(self):
        return "TightropeWalker"

    def PickMove(self, auto, world, targets, validity):
        if self.waypoints is None:
            self._plan_route(auto, world)

        # Discard waypoints we have already reached
        while self.waypoints and self.waypoints[0] == auto.pos:
            self.waypoints.pop(0)

        if not self.waypoints:
            return self._first_valid(targets, validity)

        return self._closest_to(targets, validity, self.waypoints[0])

    # ------------------------------------------------------------------

    def _plan_route(self, auto, world):
        path = _bfs(auto.pos, world.finish_vertices, world.road,
                    self.track.width, self.track.height)
        if not path:
            self.logger.warning("BFS found no path to finish – will pick randomly.")
            self.waypoints = []
            return

        tight = _tighten(path, self.track)
        self.waypoints = _bresenham_waypoints(tight)
        self.logger.info(
            "Route planned: BFS %d → tight %d → waypoints %d",
            len(path), len(tight), len(self.waypoints),
        )

    def _first_valid(self, targets, validity):
        for target, valid in zip(targets, validity):
            if valid:
                return target
        return targets[0] if targets else None

    def _closest_to(self, targets, validity, goal):
        def dist_sq(t):
            return (t.x - goal.x) ** 2 + (t.y - goal.y) ** 2

        valid_targets = [t for t, v in zip(targets, validity) if v]
        if not valid_targets:
            return self._first_valid(targets, validity)
        return min(valid_targets, key=dist_sq)


# ---------------------------------------------------------------------------
# Phase A – BFS on the vertex grid
# ---------------------------------------------------------------------------

def _vertex_on_road(road, vx, vy, cell_width, cell_height):
    """True if vertex (vx, vy) touches at least one road cell."""
    for cx in range(max(0, vx - 1), min(vx + 1, cell_width)):
        for cy in range(max(0, vy - 1), min(vy + 1, cell_height)):
            if road[cx][cy]:
                return True
    return False


def _bfs(start, finish_vertices, road, cell_width, cell_height):
    """Return a vertex-path from *start* to the nearest finish vertex, or None."""
    finish_set = {(v.x, v.y) for v in finish_vertices}

    queue = deque([start])
    # maps (x, y) → parent Vertex (None for start)
    visited = {(start.x, start.y): None}

    while queue:
        current = queue.popleft()

        if (current.x, current.y) in finish_set:
            return _reconstruct(visited, current)

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = current.x + dx, current.y + dy
                if (nx, ny) in visited:
                    continue
                if not (0 <= nx <= cell_width and 0 <= ny <= cell_height):
                    continue
                if not _vertex_on_road(road, nx, ny, cell_width, cell_height):
                    continue
                visited[(nx, ny)] = current
                queue.append(Vertex(nx, ny))

    return None


def _reconstruct(visited, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = visited[(node.x, node.y)]
    path.reverse()
    return path


# ---------------------------------------------------------------------------
# Phase B – greedy string-tightening
# ---------------------------------------------------------------------------

def _tighten(path, track):
    """Shorten *path* by skipping nodes whenever a direct segment is valid."""
    if not path:
        return []

    tight = [path[0]]
    i = 0
    while i < len(path) - 1:
        # Scan from the far end; first hit is the furthest reachable node.
        best_j = i + 1
        for j in range(len(path) - 1, i, -1):
            if track.segment_is_valid(path[i], path[j]):
                best_j = j
                break
        tight.append(path[best_j])
        i = best_j

    return tight


# ---------------------------------------------------------------------------
# Phase C – Bresenham densification
# ---------------------------------------------------------------------------

def _bresenham(x0, y0, x1, y1):
    """Integer grid points along the segment from (x0,y0) to (x1,y1)."""
    points = []
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    x, y = x0, y0

    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

    return points


def _bresenham_waypoints(tight_path):
    """Concatenate Bresenham segments; remove duplicates at join points."""
    waypoints = []
    for i in range(len(tight_path) - 1):
        p0, p1 = tight_path[i], tight_path[i + 1]
        for x, y in _bresenham(p0.x, p0.y, p1.x, p1.y):
            v = Vertex(x, y)
            if not waypoints or waypoints[-1] != v:
                waypoints.append(v)
    return waypoints
