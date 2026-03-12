"""Simple rectangular track generator.

All interior cells are track; only the border row/column is off-road.
Start: vertical strip at x=1, centered vertically.
Finish: vertical strip at x=width-2, centered vertically.
"""

import logging

_LOGGER = logging.getLogger("racecars.track_generators.rectangle")

META = {
    "id": "rectangle",
    "name": "Rectangle",
}


def generate_track(params):
    width = params["width"]
    height = params["height"]
    player_count = params["player_count"]
    seed = params["seed"]

    _LOGGER.info(
        "generate_track: id=%s, width=%d, height=%d, player_count=%d, seed=%s",
        META["id"], width, height, player_count, seed
    )

    # Build grid: all True inside, False on the outer border.
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            is_border = (x == 0 or x == width - 1 or y == 0 or y == height - 1)
            row.append(not is_border)
        grid.append(row)

    # Start nodes: vertical strip at x=1, centered vertically.
    start_count = player_count + 3
    mid_y = height // 2
    start_top = mid_y - start_count // 2
    if start_top < 1:
        start_top = 1
    if start_top + start_count > height - 1:
        start_top = height - 1 - start_count

    start_nodes = []
    for i in range(start_count):
        start_nodes.append((1, start_top + i))

    # Finish nodes: vertical line at x=width-1 (right border), centered vertically.
    # Placed on the border so cars must cross the very edge of the track to finish.
    finish_count = player_count
    if finish_count < 3:
        finish_count = 3
    finish_top = mid_y - finish_count // 2
    if finish_top < 1:
        finish_top = 1
    if finish_top + finish_count > height - 1:
        finish_top = height - 1 - finish_count

    finish_nodes = []
    for i in range(finish_count):
        finish_nodes.append((width - 1, finish_top + i))

    return grid, start_nodes, finish_nodes
