"""L-shaped track generator.

The track forms an "L":
  - Vertical segment on the left side: x = 1..strip_width, y = 1..height-2.
  - Horizontal segment on the bottom: y = height-2-strip_width+1..height-2, x = 1..width-2.
The two segments share the bottom-left corner, creating a 90-degree turn.

Start: top of the vertical segment (x=1, y=1..strip_width).
Finish: right end of the horizontal segment (x=width-2, same y-range as horizontal).
"""

import logging

_LOGGER = logging.getLogger("racecars.track_generators.l_turn")

META = {
    "id": "l_turn",
    "name": "L turn",
}


def generate_track(params):
    width = params["width"]
    height = params["height"]
    player_count = params["player_count"]
    track_width = params["track_width"]
    seed = params["seed"]

    _LOGGER.info(
        "generate_track: id=%s, width=%d, height=%d, player_count=%d, track_width=%d, seed=%s",
        META["id"], width, height, player_count, track_width, seed
    )

    # Strip width must fit at least player_count cars side by side.
    strip_width = track_width
    if strip_width < player_count:
        strip_width = player_count
    if strip_width < 1:
        strip_width = 1

    # Clamp so both segments fit inside the border (x=1..width-2, y=1..height-2).
    max_by_height = height - 3
    if strip_width > max_by_height and max_by_height >= 1:
        strip_width = max_by_height
    max_by_width = (width - 2) // 2
    if strip_width > max_by_width and max_by_width >= 1:
        strip_width = max_by_width
    if strip_width < 1:
        strip_width = 1

    # Build empty grid (all False).
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(False)
        grid.append(row)

    # Vertical segment: x = 1..strip_width, y = 1..height-2.
    vert_x_end = strip_width  # inclusive
    if vert_x_end > width - 2:
        vert_x_end = width - 2
    for y in range(1, height - 1):
        for x in range(1, vert_x_end + 1):
            grid[y][x] = True

    # Horizontal segment: y = height-2-strip_width+1..height-2, x = 1..width-2.
    horiz_y_start = height - 1 - strip_width
    if horiz_y_start < 1:
        horiz_y_start = 1
    for y in range(horiz_y_start, height - 1):
        for x in range(1, width - 1):
            grid[y][x] = True

    # Start nodes: top of vertical segment at x=1, going downward.
    start_count = strip_width
    if start_count > player_count + 3:
        start_count = player_count + 3

    start_nodes = []
    for i in range(start_count):
        start_nodes.append((1, 1 + i))

    # Finish nodes: vertical line at x=width-1 (right border).
    # Placed on the border so cars must cross the very edge of the track to finish.
    finish_count = strip_width
    if finish_count < 3:
        finish_count = 3

    finish_nodes = []
    for i in range(finish_count):
        finish_nodes.append((width - 1, horiz_y_start + i))

    return grid, start_nodes, finish_nodes
