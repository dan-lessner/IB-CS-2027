"""Snake track generator.

Generates a back-and-forth (snake) track:
  - Horizontal passes connected by smooth semicircular U-turns at each end.
  - Orientation (horizontal/vertical) is chosen randomly so start and finish
    can appear on any side of the grid.
  - Start line: as wide as (player_count + 2) to fit all players comfortably.
  - Cruise width: randomly 4-8 cells, tapering down from the opening.
  - Turn radius: randomly 10-20 cells for smooth arcs.

Return value matches the contract expected by simulation/track_runner.py:
  (grid, start_nodes, finish_nodes)
  - grid[y][x]  -- row-major 2D bool list, True = driveable
  - start_nodes -- list of (x, y) tuples ON the road
  - finish_nodes -- list of (x, y) tuples on the outer border (off-road),
                    forming a straight consecutive line
"""

import math
import random
import logging

_LOGGER = logging.getLogger("racecars.track_generators.snake")

META = {
    "id": "snake",
    "name": "Snake",
}


# ---------------------------------------------------------------------------
# Centerline sampling helpers
# ---------------------------------------------------------------------------

def _sample_line(x1, y1, x2, y2):
    """Return a list of (x, y) floats densely sampling the line from (x1,y1) to (x2,y2).

    One sample roughly every 0.5 pixels so rasterised disks overlap nicely.
    """
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)

    points = []
    if length < 0.1:
        points.append((float(x1), float(y1)))
        return points

    n = max(1, int(length * 2))
    for i in range(n + 1):
        t = i / n
        points.append((x1 + t * dx, y1 + t * dy))
    return points


def _sample_arc(cx, cy, radius, angle_start, angle_end):
    """Return a list of (x, y) floats sampling a circular arc.

    The arc runs from angle_start to angle_end (radians).
    When angle_end < angle_start the arc goes in the decreasing direction
    (useful for left-hand U-turns that sweep through pi).
    """
    arc_length = abs(angle_end - angle_start) * radius
    n = max(4, int(arc_length * 2))

    points = []
    for i in range(n + 1):
        t = i / n
        angle = angle_start + t * (angle_end - angle_start)
        points.append((cx + radius * math.cos(angle),
                       cy + radius * math.sin(angle)))
    return points


# ---------------------------------------------------------------------------
# Rasterisation helper
# ---------------------------------------------------------------------------

def _paint_disk(grid, gw, gh, cx, cy, radius):
    """Set all cells within 'radius' of (cx, cy) to True in the grid.

    Stays strictly inside the inner area (1-cell safety border excluded).
    """
    r_int = int(radius) + 1
    xi = int(round(cx))
    yi = int(round(cy))

    for dy in range(-r_int, r_int + 1):
        for dx in range(-r_int, r_int + 1):
            if dx * dx + dy * dy <= radius * radius:
                px = xi + dx
                py = yi + dy
                # Keep away from the outer border (track_runner enforces it anyway)
                if 1 <= px <= gw - 2 and 1 <= py <= gh - 2:
                    grid[py][px] = True


# ---------------------------------------------------------------------------
# Core generation (always horizontal; vertical is handled by transposing)
# ---------------------------------------------------------------------------

def _generate_horizontal(gw, gh, player_count):
    """Generate a horizontal snake track on a gw x gh grid.

    Assumes the caller has already seeded the RNG.
    Returns (grid, start_nodes, finish_nodes) in the horizontal coordinate
    system.  The caller transposes these for a vertical snake.
    """

    # --- Track parameters ---
    # Turn radius controls how wide the U-turns are (10..20 cells).
    turn_radius = random.randint(10, 20)
    # Cruise width is the track width after the opening section (4..8 cells).
    cruise_width = random.randint(4, 8)
    # Opening is wide enough for all players plus two spare cells.
    start_width = player_count + 2

    half_cw = cruise_width // 2   # half cruise width (used as disk radius)
    half_sw = start_width // 2    # half start width

    # --- Inner grid bounds (1-cell border excluded) ---
    x_min = 1
    x_max = gw - 2
    y_min = 1
    y_max = gh - 2

    # --- U-turn column positions ---
    # A right U-turn is a semicircle that bulges to the RIGHT.
    # Its centre sits at x_right_col; the rightmost point reaches
    # x_right_col + turn_radius, which must not exceed x_max - half_cw.
    x_right_col = x_max - turn_radius - half_cw - 1

    # A left U-turn bulges to the LEFT; leftmost point = x_left_col - turn_radius.
    x_left_col = x_min + turn_radius + half_cw + 1

    # Safety: if the grid is too narrow just split it evenly.
    if x_right_col <= x_left_col:
        quarter = (x_max - x_min) // 4
        x_left_col  = x_min + quarter
        x_right_col = x_max - quarter

    # --- Lane spacing = diameter of one U-turn circle ---
    # Adjacent lanes must be exactly 2*turn_radius apart so the semicircle
    # connects them perfectly.
    lane_spacing = turn_radius * 2

    # --- Compute lane Y positions ---
    # Start close to the top wall, leaving half_cw clearance.
    first_lane_y = y_min + half_cw + 2

    lanes_y = []
    y = first_lane_y
    while y + half_cw + 2 <= y_max:
        lanes_y.append(y)
        y = y + lane_spacing

    # At least two lanes are needed for the snake shape.
    if len(lanes_y) < 2:
        quarter_h = (y_max - y_min) // 4
        lanes_y = [y_min + quarter_h, y_max - quarter_h]

    n_lanes = len(lanes_y)

    # --- Build the centerline path ---
    # Lane 0 goes left-to-right, lane 1 goes right-to-left, and so on.
    # Each lane is a straight segment plus a U-turn arc at its far end.
    centerline = []

    for i in range(n_lanes):
        lane_y = lanes_y[i]
        going_right = (i % 2 == 0)

        # X coordinate where this straight segment starts.
        if i == 0:
            # First lane: begin at the inner-left edge.
            x_from = x_min
        elif going_right:
            # Exiting a left U-turn.
            x_from = x_left_col
        else:
            # Exiting a right U-turn.
            x_from = x_right_col

        # X coordinate where this straight segment ends.
        if i == n_lanes - 1:
            # Last lane: exit to the appropriate inner edge.
            if going_right:
                x_to = x_max
            else:
                x_to = x_min
        elif going_right:
            # Heading into a right U-turn.
            x_to = x_right_col
        else:
            # Heading into a left U-turn.
            x_to = x_left_col

        # Sample the straight segment.
        seg_pts = _sample_line(x_from, lane_y, x_to, lane_y)
        centerline.extend(seg_pts)

        # Add the U-turn arc to the next lane (skip for the last lane).
        if i < n_lanes - 1:
            y_next = lanes_y[i + 1]
            # Centre of the connecting semicircle, vertically midway.
            y_mid = (lane_y + y_next) / 2.0

            if going_right:
                # RIGHT U-turn: the arc bulges to the right (+x direction).
                # Standard math angles (y-down screen coords):
                #   angle -pi/2  -> top of circle    -> point (cx,   cy-r) = lane_y
                #   angle  pi/2  -> bottom of circle -> point (cx,   cy+r) = y_next
                #   angle  0     -> rightmost point  -> bulge
                # Going from -pi/2 to +pi/2 (increasing) sweeps the right half. ✓
                arc_pts = _sample_arc(
                    x_right_col, y_mid, turn_radius,
                    -math.pi / 2, math.pi / 2
                )
            else:
                # LEFT U-turn: the arc bulges to the left (-x direction).
                #   angle -pi/2  -> (cx, cy-r) = lane_y
                #   angle -3pi/2 -> same as pi/2 -> (cx, cy+r) = y_next
                #   angle -pi    -> leftmost point -> bulge
                # Going from -pi/2 to -3pi/2 (decreasing) sweeps the left half. ✓
                arc_pts = _sample_arc(
                    x_left_col, y_mid, turn_radius,
                    -math.pi / 2, -3 * math.pi / 2
                )

            centerline.extend(arc_pts)

    # --- Rasterise centerline onto the grid ---
    grid = []
    for row in range(gh):
        grid_row = []
        for col in range(gw):
            grid_row.append(False)
        grid.append(grid_row)

    total_pts = len(centerline)
    # Taper track width from half_sw at the opening to half_cw at cruise speed.
    # The taper runs over the first (start_width * 4) centerline samples.
    taper_len = max(1, start_width * 4)

    for idx in range(total_pts):
        cx, cy = centerline[idx]

        if idx < taper_len:
            # Linear interpolation from half_sw down to half_cw.
            t = idx / taper_len
            disk_r = half_sw + t * (half_cw - half_sw)
        else:
            disk_r = float(half_cw)

        _paint_disk(grid, gw, gh, cx, cy, disk_r)

    # --- Start nodes ---
    # A vertical strip of on-road cells at x = x_min, centred on the first lane.
    # These cells are always on the road because the first centerline sample is
    # at (x_min, lanes_y[0]) and the opening disk has radius half_sw.
    start_nodes = []
    for dy in range(-half_sw, half_sw + 1):
        py = lanes_y[0] + dy
        if y_min <= py <= y_max:
            start_nodes.append((x_min, py))

    # --- Finish nodes ---
    # Placed on the OUTER border (one step past the road), as required by
    # track_runner: BFS checks adjacency to finish nodes, not membership.
    #   last lane goes right -> outer right border (x = gw - 1)
    #   last lane goes left  -> outer left border  (x = 0)
    last_going_right = ((n_lanes - 1) % 2 == 0)
    if last_going_right:
        x_finish = gw - 1
    else:
        x_finish = 0

    finish_nodes = []
    for dy in range(-half_cw, half_cw + 1):
        py = lanes_y[n_lanes - 1] + dy
        if 0 <= py <= gh - 1:
            finish_nodes.append((x_finish, py))

    return grid, start_nodes, finish_nodes


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_track(params):
    width  = params["width"]
    height = params["height"]
    player_count = params["player_count"]
    seed   = params["seed"]

    _LOGGER.info(
        "generate_track: id=%s, width=%d, height=%d, players=%d, seed=%s",
        META["id"], width, height, player_count, seed
    )

    # Pick orientation randomly.
    # For a horizontal snake the passes run left-to-right.
    # For a vertical snake we generate horizontally on a transposed grid and
    # then flip coordinates back so the passes run top-to-bottom.
    if seed is not None:
        random.seed(seed)
    horizontal = random.choice([True, False])

    if horizontal:
        # Generate directly on the real grid dimensions.
        grid, start_nodes, finish_nodes = _generate_horizontal(
            width, height, player_count
        )
        return grid, start_nodes, finish_nodes

    # --- Vertical snake ---
    # Generate a horizontal snake on a (height x width) canvas, then transpose.
    # Inside _generate_horizontal: gw=height, gh=width.
    gen_grid, gen_start, gen_finish = _generate_horizontal(
        height, width, player_count
    )

    # Transpose the grid.
    # gen_grid[r][c] lives in (gw=height) x (gh=width) space.
    # We want game_grid[game_y][game_x] = gen_grid[game_x][game_y]
    # because generated-x becomes game-y and generated-y becomes game-x.
    game_grid = []
    for game_y in range(height):
        row = []
        for game_x in range(width):
            # gen_grid row = game_x (in 0..width-1 = gh-1)
            # gen_grid col = game_y (in 0..height-1 = gw-1)
            row.append(gen_grid[game_x][game_y])
        game_grid.append(row)

    # Transpose node coordinates: generated (gx, gy) -> game (gy, gx).
    game_start = []
    for gx, gy in gen_start:
        game_start.append((gy, gx))

    game_finish = []
    for gx, gy in gen_finish:
        game_finish.append((gy, gx))

    return game_grid, game_start, game_finish
