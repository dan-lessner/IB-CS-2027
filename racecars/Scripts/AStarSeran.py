"""
A* over the state space (x, y, vx, vy) to find minimum-step path to finish.

State:  (x, y, vx, vy) -- grid position and velocity
Action: (ax, ay) each in {-1, 0, 1}  -- 9 possible accelerations
Cost:   1 per step (we minimise step count)
Heuristic: per-axis formula from spec, take max of both axes.

Targets list from the engine is ordered ax in [-1,0,1], ay in [-1,0,1],
so target_index = (ax+1)*3 + (ay+1) maps an acceleration to its target.
"""

import heapq
import math
from simulation.script_api import AutoAuto


# ---------------------------------------------------------------------------
# Driving-style score functions for tie-breaking.
# Smaller value = preferred when f = g + h is equal.
# To switch style, reassign move_style_score below the function definitions.
# ---------------------------------------------------------------------------

def _score_smooth(vx2, vy2, vx, vy):
    """Prefer smooth driving: minimise angle change (maximise cosine)."""
    len_prev = math.sqrt(vx * vx + vy * vy)
    len_next = math.sqrt(vx2 * vx2 + vy2 * vy2)
    if len_prev < 0.001 or len_next < 0.001:
        return 0.0
    cos_angle = (vx * vx2 + vy * vy2) / (len_prev * len_next)
    # Smaller value preferred; smaller cos_angle = larger turn => use -cos
    return -cos_angle


def _score_max_speed(vx2, vy2, vx, vy):
    """Prefer higher speed."""
    speed = math.sqrt(vx2 * vx2 + vy2 * vy2)
    return -speed  # negative so higher speed = smaller value = preferred


def _score_min_speed(vx2, vy2, vx, vy):
    """Prefer lower speed."""
    speed = math.sqrt(vx2 * vx2 + vy2 * vy2)
    return speed


def _score_zigzag(vx2, vy2, vx, vy):
    """Prefer large angle changes (zigzag style)."""
    len_prev = math.sqrt(vx * vx + vy * vy)
    len_next = math.sqrt(vx2 * vx2 + vy2 * vy2)
    if len_prev < 0.001 or len_next < 0.001:
        return 0.0
    cos_angle = (vx * vx2 + vy * vy2) / (len_prev * len_next)
    return cos_angle  # larger angle = smaller cos = lower value when not negated


# Change this variable to switch driving style (affects tie-breaking only):
move_style_score = _score_max_speed


class Auto(AutoAuto):

    def __init__(self, track):
        super().__init__()
        self.track = track  # Track object, available for reference

        # Plan: list of (ax, ay) tuples; plan_index = next action to execute
        self.plan = []
        self.plan_index = 0

        # Expected state at next PickMove call (used to detect deviations)
        self.expected_x = None
        self.expected_y = None
        self.expected_vx = None
        self.expected_vy = None

        # Cached world data, filled on first PickMove call
        self.road = None         # road_mask: road[cx][cy] == True means road cell
        self.road_width = 0
        self.road_height = 0
        self.finish_set = None   # dict (x, y) -> True for all finish vertices
        self.max_speed = 20      # per-axis speed limit derived from map size

        # Finish line geometry (derived from finish_set to detect crossings)
        self.finish_is_vertical = False  # True = same x; False = same y
        self.finish_fixed = 0            # the x (vertical) or y (horizontal) coord
        self.finish_range_min = 0        # min y (vertical) or x (horizontal)
        self.finish_range_max = 0        # max y (vertical) or x (horizontal)

        self.logger.info("AStarSeran initialised.")

    def GetName(self):
        return "A* Seran"

    # ------------------------------------------------------------------
    # PickMove -- called once per turn; must return a Vertex from targets
    # ------------------------------------------------------------------

    def PickMove(self, auto, world, targets, validity):
        pos_x = int(auto.pos.x)
        pos_y = int(auto.pos.y)
        vel_x = int(auto.vel.x)
        vel_y = int(auto.vel.y)

        # One-time initialisation of road/finish data
        if self.road is None:
            self._init_world(world)

        # Replan if we deviated from the expected trajectory, or plan ran out
        state_ok = self._state_matches_expected(pos_x, pos_y, vel_x, vel_y)
        has_actions = (self.plan_index < len(self.plan))

        if not state_ok or not has_actions:
            self.logger.info(
                "Computing A* plan from (%d,%d) vel=(%d,%d).",
                pos_x, pos_y, vel_x, vel_y
            )
            new_plan = self._run_astar(pos_x, pos_y, vel_x, vel_y)
            if new_plan is None or len(new_plan) == 0:
                self.logger.warning("A* found no path, falling back to first valid target.")
                return self._first_valid(targets, validity)
            self.plan = new_plan
            self.plan_index = 0

        # Consume next planned action
        action = self.plan[self.plan_index]
        ax = action[0]
        ay = action[1]
        self.plan_index = self.plan_index + 1

        # Remember what state we expect next turn so we can detect deviations
        new_vx = vel_x + ax
        new_vy = vel_y + ay
        self.expected_x = pos_x + new_vx
        self.expected_y = pos_y + new_vy
        self.expected_vx = new_vx
        self.expected_vy = new_vy

        # Map acceleration to index in the engine-generated targets list:
        # engine loops ax in [-1,0,1] outer, ay in [-1,0,1] inner
        target_index = (ax + 1) * 3 + (ay + 1)

        if target_index < len(targets) and validity[target_index]:
            return targets[target_index]

        # Planned move is blocked (e.g. another car); invalidate plan and
        # return the first available safe move this turn
        self.logger.info(
            "Planned move (ax=%d, ay=%d) blocked; will replan next turn.", ax, ay
        )
        self.expected_x = None  # force replanning on next call
        return self._first_valid(targets, validity)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_world(self, world):
        self.road = world.road
        self.road_width = len(world.road)
        if self.road_width > 0:
            self.road_height = len(world.road[0])

        # Build finish lookup dict
        self.finish_set = {}
        for v in world.finish_vertices:
            self.finish_set[(v.x, v.y)] = True

        # Speed limit: largest speed reachable on this map (spec section 9.1)
        bigger = self.road_width
        if self.road_height > bigger:
            bigger = self.road_height
        self.max_speed = int(math.sqrt(1 + 8 * bigger) / 2) + 1

        # Determine finish line orientation and extent
        self._analyse_finish_line()

    def _analyse_finish_line(self):
        """Determine if finish line is vertical or horizontal, and its extent."""
        # Check whether all finish vertices share the same x (vertical line)
        first_x = None
        all_same_x = True
        for key in self.finish_set:
            if first_x is None:
                first_x = key[0]
            elif key[0] != first_x:
                all_same_x = False
                break

        if all_same_x and first_x is not None:
            # Vertical finish line: fixed x, varying y
            self.finish_is_vertical = True
            self.finish_fixed = first_x
            y_min = None
            y_max = None
            for key in self.finish_set:
                ky = key[1]
                if y_min is None or ky < y_min:
                    y_min = ky
                if y_max is None or ky > y_max:
                    y_max = ky
            self.finish_range_min = y_min
            self.finish_range_max = y_max
        else:
            # Horizontal finish line: fixed y, varying x
            self.finish_is_vertical = False
            first_y = None
            for key in self.finish_set:
                if first_y is None:
                    first_y = key[1]
            self.finish_fixed = first_y
            x_min = None
            x_max = None
            for key in self.finish_set:
                kx = key[0]
                if x_min is None or kx < x_min:
                    x_min = kx
                if x_max is None or kx > x_max:
                    x_max = kx
            self.finish_range_min = x_min
            self.finish_range_max = x_max

    # ------------------------------------------------------------------
    # A* search
    # ------------------------------------------------------------------

    def _run_astar(self, start_x, start_y, start_vx, start_vy):
        """
        A* search on (x, y, vx, vy) state space.
        Returns list of (ax, ay) actions from start to goal, or None.
        """
        start_state = (start_x, start_y, start_vx, start_vy)

        # g_best[state] = best known step count from start to state
        g_best = {}
        g_best[start_state] = 0

        # came_from[state] = (parent_state, action) for path reconstruction
        came_from = {}

        h_start = self._heuristic(start_x, start_y, start_vx, start_vy)

        # Min-heap: entries are (f_value, tiebreak_counter, state_tuple)
        heap = []
        counter = 0
        heapq.heappush(heap, (h_start, counter, start_state))

        # closed[state] = True once fully expanded (lazy deletion from heap)
        closed = {}

        while len(heap) > 0:
            entry = heapq.heappop(heap)
            state = entry[2]

            # Lazy deletion: already expanded with a better g
            if state in closed:
                continue
            closed[state] = True

            x = state[0]
            y = state[1]
            vx = state[2]
            vy = state[3]
            current_g = g_best[state]

            # Goal: landed on a finish cell
            if (x, y) in self.finish_set:
                return self._reconstruct_actions(came_from, state)

            # Expand all 9 accelerations
            for ax in [-1, 0, 1]:
                for ay in [-1, 0, 1]:
                    vx2 = vx + ax
                    vy2 = vy + ay

                    # Per-axis speed limit (spec section 9.1)
                    if abs(vx2) > self.max_speed or abs(vy2) > self.max_speed:
                        continue

                    x2 = x + vx2
                    y2 = y + vy2

                    # Bounds check (vertices go from 0 to width/height inclusive)
                    if x2 < 0 or x2 > self.road_width:
                        continue
                    if y2 < 0 or y2 > self.road_height:
                        continue

                    # Check if segment crosses finish line (car may overshoot)
                    finish_crossing = self._finish_crossing_vertex(x, y, x2, y2)
                    if finish_crossing is not None:
                        # Redirect to the finish vertex the engine would snap to
                        x2 = finish_crossing[0]
                        y2 = finish_crossing[1]
                        # No further road check needed: finish vertex is on track
                    else:
                        # Destination must be on road
                        if not self._vertex_is_inside(x2, y2):
                            continue
                        # Whole segment must stay on road
                        if not self._segment_is_valid(x, y, x2, y2):
                            continue

                    next_state = (x2, y2, vx2, vy2)

                    if next_state in closed:
                        continue

                    tentative_g = current_g + 1

                    best_so_far = g_best.get(next_state, 999999999)
                    if tentative_g >= best_so_far:
                        continue

                    g_best[next_state] = tentative_g
                    came_from[next_state] = (state, (ax, ay))

                    h = self._heuristic(x2, y2, vx2, vy2)
                    # Style score as a tiny secondary key (does not affect step count)
                    style = move_style_score(vx2, vy2, vx, vy)
                    f_next = tentative_g + h + style * 0.00001
                    counter = counter + 1
                    heapq.heappush(heap, (f_next, counter, next_state))

        return None  # No path found

    def _reconstruct_actions(self, came_from, goal_state):
        """Walk back from goal to start collecting actions; return in forward order."""
        actions = []
        state = goal_state
        while state in came_from:
            parent_and_action = came_from[state]
            action = parent_and_action[1]
            actions.append(action)
            state = parent_and_action[0]

        # Build result list in forward order (actions were collected backwards)
        result = []
        i = len(actions) - 1
        while i >= 0:
            result.append(actions[i])
            i = i - 1
        return result

    # ------------------------------------------------------------------
    # Heuristic (admissible lower bound on remaining steps)
    # ------------------------------------------------------------------

    def _heuristic(self, x, y, vx, vy):
        """
        Find nearest finish cell, then compute per-axis lower bounds.
        Returns the larger of the two axes (bottleneck).
        """
        best_dist_sq = None
        best_fx = x
        best_fy = y
        for key in self.finish_set:
            fx = key[0]
            fy = key[1]
            ddx = fx - x
            ddy = fy - y
            dist_sq = ddx * ddx + ddy * ddy
            if best_dist_sq is None or dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best_fx = fx
                best_fy = fy

        if best_dist_sq is None:
            return 0

        hx = self._heuristic_1d(best_fx - x, vx)
        hy = self._heuristic_1d(best_fy - y, vy)

        if hx > hy:
            return hx
        return hy

    def _heuristic_1d(self, d_raw, v_raw):
        """
        Minimum steps to travel d_raw cells with starting velocity v_raw
        along a single axis, with acceleration in {-1, 0, +1} per step.

        Step 1: Make d non-negative by flipping direction if needed.
                After flip, d >= 0 and v tells us if we move toward (v > 0)
                or away from (v < 0) the goal.
        Step 2: Apply formula (spec section 7):
                h = -v + sqrt((2*v - 1)^2 + 8*d) / 2
        Step 3: Clamp to 0 (result can be slightly negative for reachable goals).
        """
        d = d_raw
        v = v_raw

        # Align: ensure d >= 0; flip both signs when d < 0
        if d < 0:
            d = -d
            v = -v
        # Now d >= 0; v > 0 = moving toward goal, v < 0 = moving away

        under_sqrt = (2 * v - 1) * (2 * v - 1) + 8 * d
        if under_sqrt < 0.0:
            under_sqrt = 0.0

        h = -v + math.sqrt(under_sqrt) / 2.0

        if h < 0.0:
            h = 0.0
        return h

    # ------------------------------------------------------------------
    # Finish line crossing detection
    # ------------------------------------------------------------------

    def _finish_crossing_vertex(self, x0, y0, x1, y1):
        """
        Check if segment (x0,y0)->(x1,y1) crosses the finish line.
        Returns (fx, fy) of the nearest finish vertex on the line, or None.
        Mirrors the engine's finish_vertex_for_segment logic.
        """
        if self.finish_is_vertical:
            fx = self.finish_fixed
            # Segment must cross x = fx
            if x0 == x1:
                # Parallel to finish line
                if x0 != fx:
                    return None
                # Already on finish line -- snap y to nearest finish vertex in range
                cross_y = y1
            else:
                # Compute crossing parameter t
                t = (fx - x0) / (x1 - x0)
                if t < 0.0 or t > 1.0:
                    return None
                cross_y = y0 + (y1 - y0) * t
            # Check crossing point is within finish range
            if cross_y < self.finish_range_min or cross_y > self.finish_range_max:
                return None
            # Snap to nearest integer finish vertex
            fy = int(round(cross_y))
            if fy < self.finish_range_min:
                fy = self.finish_range_min
            if fy > self.finish_range_max:
                fy = self.finish_range_max
            if (fx, fy) in self.finish_set:
                return (fx, fy)
            return None
        else:
            fy = self.finish_fixed
            # Segment must cross y = fy
            if y0 == y1:
                # Parallel to finish line
                if y0 != fy:
                    return None
                cross_x = x1
            else:
                t = (fy - y0) / (y1 - y0)
                if t < 0.0 or t > 1.0:
                    return None
                cross_x = x0 + (x1 - x0) * t
            if cross_x < self.finish_range_min or cross_x > self.finish_range_max:
                return None
            fx = int(round(cross_x))
            if fx < self.finish_range_min:
                fx = self.finish_range_min
            if fx > self.finish_range_max:
                fx = self.finish_range_max
            if (fx, fy) in self.finish_set:
                return (fx, fy)
            return None

    # ------------------------------------------------------------------
    # Road / segment helpers (replicate engine logic via world.road mask)
    # ------------------------------------------------------------------

    def _vertex_is_inside(self, vx, vy):
        """A vertex is on-road if any of its adjacent cells is road."""
        for cx in range(vx - 1, vx + 1):
            for cy in range(vy - 1, vy + 1):
                if 0 <= cx < self.road_width and 0 <= cy < self.road_height:
                    if self.road[cx][cy]:
                        return True
        return False

    def _point_is_on_road(self, x_f, y_f):
        """
        Check if a float-coordinate point is on road.
        A point is valid if any cell it touches (including at exact integer
        boundaries) is road. Matches engine's _sample_point_is_on_road.
        """
        if x_f < 0 or y_f < 0 or x_f > self.road_width or y_f > self.road_height:
            return False

        epsilon = 0.000001
        base_x = int(x_f)
        base_y = int(y_f)

        # At exact integer coords the point touches adjacent cells too
        cells_x = [base_x]
        if abs(x_f - round(x_f)) < epsilon:
            cells_x.append(base_x - 1)

        cells_y = [base_y]
        if abs(y_f - round(y_f)) < epsilon:
            cells_y.append(base_y - 1)

        for cx in cells_x:
            for cy in cells_y:
                if 0 <= cx < self.road_width and 0 <= cy < self.road_height:
                    if self.road[cx][cy]:
                        return True
        return False

    def _segment_is_valid(self, x0, y0, x1, y1):
        """
        Check that the segment (x0,y0)->(x1,y1) stays on road.
        Collects all t-values where the segment crosses a grid line, then
        checks the midpoint of every resulting interval. Matches engine logic.
        """
        dx = x1 - x0
        dy = y1 - y0

        if dx == 0 and dy == 0:
            return self._point_is_on_road(float(x0), float(y0))

        # Collect t-values at grid crossings (vertical and horizontal lines)
        t_values = []
        t_values.append(0.0)
        t_values.append(1.0)

        if dx > 0:
            x_cross = x0 + 1
            while x_cross < x1:
                t = (x_cross - x0) / dx
                if t > 0.0 and t < 1.0:
                    t_values.append(t)
                x_cross = x_cross + 1
        elif dx < 0:
            x_cross = x0 - 1
            while x_cross > x1:
                t = (x_cross - x0) / dx
                if t > 0.0 and t < 1.0:
                    t_values.append(t)
                x_cross = x_cross - 1

        if dy > 0:
            y_cross = y0 + 1
            while y_cross < y1:
                t = (y_cross - y0) / dy
                if t > 0.0 and t < 1.0:
                    t_values.append(t)
                y_cross = y_cross + 1
        elif dy < 0:
            y_cross = y0 - 1
            while y_cross > y1:
                t = (y_cross - y0) / dy
                if t > 0.0 and t < 1.0:
                    t_values.append(t)
                y_cross = y_cross - 1

        # Insertion sort (readable, no library tricks)
        n = len(t_values)
        for i in range(1, n):
            key = t_values[i]
            j = i - 1
            while j >= 0 and t_values[j] > key:
                t_values[j + 1] = t_values[j]
                j = j - 1
            t_values[j + 1] = key

        # Check midpoint of each interval between consecutive t-values
        epsilon = 0.0000001
        for i in range(len(t_values) - 1):
            t0 = t_values[i]
            t1 = t_values[i + 1]
            if t1 - t0 <= epsilon:
                continue
            t_mid = (t0 + t1) * 0.5
            x_mid = x0 + dx * t_mid
            y_mid = y0 + dy * t_mid
            if not self._point_is_on_road(x_mid, y_mid):
                return False

        return True

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _state_matches_expected(self, pos_x, pos_y, vel_x, vel_y):
        """True iff current state matches the state predicted after the last move."""
        if self.expected_x is None:
            return False
        if pos_x != self.expected_x or pos_y != self.expected_y:
            return False
        if vel_x != self.expected_vx or vel_y != self.expected_vy:
            return False
        return True

    def _first_valid(self, targets, validity):
        """Return the first valid target, or targets[0] as an emergency fallback."""
        for i in range(len(targets)):
            if validity[i]:
                return targets[i]
        return targets[0]
