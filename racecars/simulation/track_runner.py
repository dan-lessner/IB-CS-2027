"""Post-processing and validation for track generator scripts.

Calls generate_track(params) on a loaded TrackGeneratorInfo module,
enforces the safety border, validates start/finish nodes, checks BFS
connectivity, and converts the result to a Track object.
"""

import logging
from simulation.game_state import Track, Vertex, Segment

_LOGGER = logging.getLogger("racecars.track_runner")

MAX_ATTEMPTS = 200


def build_track_from_generator(generator_info, params):
    """Call the generator script and apply post-processing. Returns a Track."""
    params_dict = _build_params_dict(params)

    attempt = 0
    while True:
        attempt += 1
        track = _try_generate(generator_info, params_dict)
        if track is not None:
            return track

        _LOGGER.error(
            "Track validation failed (attempt %d) for generator '%s'. Retrying.",
            attempt, generator_info.id
        )
        if attempt >= MAX_ATTEMPTS:
            _LOGGER.error(
                "Generator '%s': exceeded %d attempts. Using fallback track.",
                generator_info.id, MAX_ATTEMPTS
            )
            return _build_fallback_track(params_dict)


def _try_generate(generator_info, params_dict):
    width = params_dict["width"]
    height = params_dict["height"]
    player_count = params_dict["player_count"]

    try:
        raw = generator_info.module.generate_track(params_dict)
    except Exception as ex:
        _LOGGER.exception(
            "generate_track() raised in generator '%s' (%s: %s).",
            generator_info.id, type(ex).__name__, ex
        )
        return None

    if raw is None or len(raw) != 3:
        _LOGGER.error("Generator '%s' returned unexpected result (expected tuple of 3).", generator_info.id)
        return None

    grid = raw[0]
    start_nodes = raw[1]
    finish_nodes = raw[2]

    # 4.1: Enforce border - outer perimeter must be off-road.
    _enforce_border(grid, width, height)

    # 4.2: Validate start and finish node constraints.
    if not _validate_nodes(grid, width, height, start_nodes, finish_nodes, player_count, generator_info.id):
        return None

    # 4.3: BFS connectivity - every start node must reach some finish node.
    if not _check_connectivity(grid, width, height, start_nodes, finish_nodes):
        _LOGGER.error(
            "Generator '%s': no path from start to finish.", generator_info.id
        )
        return None

    return _build_track(grid, width, height, start_nodes, finish_nodes)


def _build_params_dict(params):
    track_width = params.track_width_mean
    if track_width < 1:
        track_width = 1
    return {
        "width": params.width,
        "height": params.height,
        "player_count": params.players,
        "track_width": track_width,
        "seed": params.seed,
        "extra": {
            "track_width_var": params.track_width_var,
            "turn_sharpness": params.turn_sharpness,
            "turn_density": params.turn_density,
        },
    }


def _enforce_border(grid, width, height):
    for x in range(width):
        grid[0][x] = False
        grid[height - 1][x] = False
    for y in range(height):
        grid[y][0] = False
        grid[y][width - 1] = False


def _validate_nodes(grid, width, height, start_nodes, finish_nodes, player_count, generator_id):
    # Check minimum start node count.
    if len(start_nodes) < player_count:
        _LOGGER.error(
            "Generator '%s': too few start nodes (%d), need at least %d.",
            generator_id, len(start_nodes), player_count
        )
        return False

    # Check all start nodes are on the track.
    for node in start_nodes:
        x = node[0]
        y = node[1]
        if x < 0 or x >= width or y < 0 or y >= height:
            _LOGGER.error("Generator '%s': start node (%d, %d) out of bounds.", generator_id, x, y)
            return False
        if not grid[y][x]:
            _LOGGER.error("Generator '%s': start node (%d, %d) is not on the track.", generator_id, x, y)
            return False

    # Check at least one finish node exists.
    if len(finish_nodes) < 1:
        _LOGGER.error("Generator '%s': no finish nodes.", generator_id)
        return False

    # Check all finish nodes are within grid bounds (they may be on the border).
    for node in finish_nodes:
        x = node[0]
        y = node[1]
        if x < 0 or x >= width or y < 0 or y >= height:
            _LOGGER.error("Generator '%s': finish node (%d, %d) out of bounds.", generator_id, x, y)
            return False

    # Check finish nodes form a connected line (all same x or all same y, consecutive).
    if not _finish_nodes_are_adjacent(finish_nodes):
        _LOGGER.error("Generator '%s': finish nodes are not a straight adjacent line.", generator_id)
        return False

    return True


def _finish_nodes_are_adjacent(nodes):
    if len(nodes) <= 1:
        return True

    x0 = nodes[0][0]
    y0 = nodes[0][1]
    all_same_x = True
    all_same_y = True

    for node in nodes:
        if node[0] != x0:
            all_same_x = False
        if node[1] != y0:
            all_same_y = False

    if not all_same_x and not all_same_y:
        return False

    # Check coordinates are consecutive (no gaps).
    if all_same_x:
        values = []
        for node in nodes:
            values.append(node[1])
        values.sort()
        for i in range(len(values) - 1):
            if values[i + 1] - values[i] > 1:
                return False
    else:
        values = []
        for node in nodes:
            values.append(node[0])
        values.sort()
        for i in range(len(values) - 1):
            if values[i + 1] - values[i] > 1:
                return False

    return True


def _check_connectivity(grid, width, height, start_nodes, finish_nodes):
    # BFS from all start nodes; return True if any visited cell is adjacent to a finish node.
    # Finish nodes are placed on the border (off-road), so we check adjacency instead of membership.
    finish_set = set()
    for node in finish_nodes:
        finish_set.add((node[0], node[1]))

    visited = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(False)
        visited.append(row)

    queue = []
    for node in start_nodes:
        x = node[0]
        y = node[1]
        if not visited[y][x]:
            visited[y][x] = True
            queue.append((x, y))

    index = 0
    while index < len(queue):
        cell = queue[index]
        index += 1
        cx = cell[0]
        cy = cell[1]

        # Check if this cell is adjacent to any finish node.
        neighbors = [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]
        for neighbor in neighbors:
            if (neighbor[0], neighbor[1]) in finish_set:
                return True

        # Expand BFS to on-track neighbors.
        for neighbor in neighbors:
            nx = neighbor[0]
            ny = neighbor[1]
            if nx < 0 or nx >= width or ny < 0 or ny >= height:
                continue
            if visited[ny][nx]:
                continue
            if not grid[ny][nx]:
                continue
            visited[ny][nx] = True
            queue.append((nx, ny))

    return False


def _build_track(grid, width, height, start_nodes, finish_nodes):
    # Convert grid[y][x] (row-major) to road_mask[x][y] (column-major) used by Track.
    road_mask = []
    for x in range(width):
        col = []
        for y in range(height):
            col.append(grid[y][x])
        road_mask.append(col)

    start_vertices = []
    for node in start_nodes:
        start_vertices.append(Vertex(node[0], node[1]))

    finish_line = _finish_nodes_to_segment(finish_nodes, width, height)

    return Track(width, height, road_mask, start_vertices, finish_line)


def _finish_nodes_to_segment(finish_nodes, width, height):
    # Generators place finish_nodes directly on the border, so we use them as-is.
    if len(finish_nodes) == 1:
        x = finish_nodes[0][0]
        y = finish_nodes[0][1]
        return Segment(Vertex(x, y), Vertex(x, y))

    x0 = finish_nodes[0][0]
    min_x = x0
    max_x = x0
    min_y = finish_nodes[0][1]
    max_y = min_y

    for node in finish_nodes:
        x = node[0]
        y = node[1]
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y

    return Segment(Vertex(min_x, min_y), Vertex(max_x, max_y))


def _build_fallback_track(params_dict):
    width = params_dict["width"]
    height = params_dict["height"]

    road_mask = []
    for x in range(width):
        col = []
        for y in range(height):
            is_border = (x == 0 or x == width - 1 or y == 0 or y == height - 1)
            col.append(not is_border)
        road_mask.append(col)

    mid_y = height // 2
    start_vertices = [Vertex(1, mid_y)]
    finish_line = Segment(Vertex(width - 2, mid_y), Vertex(width - 2, mid_y))

    return Track(width, height, road_mask, start_vertices, finish_line)
