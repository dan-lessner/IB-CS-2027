"""Simulation runner - drives the game loop without any graphics dependency.

The core race loop lives here so it can run both with a renderer (GUI mode)
and without one (headless mode). The renderer is an optional argument;
when it is None the race runs silently and exits as soon as it finishes.

Ranking system
--------------
To rank cars in real time we pre-compute a BFS (Breadth-First Search) distance
map at race start.  Starting from every vertex on the finish line, we expand
outward one grid step at a time and record how many steps each vertex is from
the finish.  Smaller distance = closer to the finish = higher rank.

After every move we walk the car list, look up each car's BFS distance, and
write the sorted result into game_state.rankings so the renderer can display
a live leaderboard.
"""

import logging
from collections import deque
from simulation.controller import Controller

_LOGGER = logging.getLogger("racecars.runner")


# ---------------------------------------------------------------------------
# BFS helpers
# ---------------------------------------------------------------------------

def _vertex_touches_road(track, vx: int, vy: int) -> bool:
    """Return True if vertex (vx, vy) is adjacent to at least one road cell.

    A vertex sits at the corner of up to four cells.  We check all four and
    return True as soon as we find one that is on the road.
    """
    for cx, cy in [(vx - 1, vy - 1), (vx, vy - 1), (vx - 1, vy), (vx, vy)]:
        if 0 <= cx < track.width and 0 <= cy < track.height:
            if track.road_mask[cx][cy]:
                return True
    return False


def _compute_bfs_dist(track):
    """Build a 2-D BFS distance array from the finish line.

    Returns a list-of-lists ``dist`` where ``dist[x][y]`` is the minimum
    number of grid steps from vertex (x, y) to any finish-line vertex.
    Vertices that are completely off-road get distance -1 (unreachable).

    Parameters
    ----------
    track : Track
        The track whose finish_line and road_mask are used.

    Returns
    -------
    list[list[int]]
        dist[x][y] for 0 <= x <= track.width, 0 <= y <= track.height.
    """
    width = track.width
    height = track.height

    # Initialise all distances as -1 (unreachable).
    dist = [[-1] * (height + 1) for _ in range(width + 1)]

    queue = deque()

    # Seed the BFS with every vertex that lies on the finish line.
    fl = track.finish_line
    if fl.start.x == fl.end.x:
        # Vertical finish line — iterate over y.
        x = fl.start.x
        y0 = min(fl.start.y, fl.end.y)
        y1 = max(fl.start.y, fl.end.y)
        for y in range(y0, y1 + 1):
            if 0 <= x <= width and 0 <= y <= height:
                dist[x][y] = 0
                queue.append((x, y))
    else:
        # Horizontal finish line — iterate over x.
        y = fl.start.y
        x0 = min(fl.start.x, fl.end.x)
        x1 = max(fl.start.x, fl.end.x)
        for x in range(x0, x1 + 1):
            if 0 <= x <= width and 0 <= y <= height:
                dist[x][y] = 0
                queue.append((x, y))

    # Standard 4-connected BFS expansion.
    while queue:
        x, y = queue.popleft()
        for nx, ny in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
            if nx < 0 or nx > width or ny < 0 or ny > height:
                continue
            if dist[nx][ny] != -1:
                continue  # Already visited.
            if _vertex_touches_road(track, nx, ny):
                dist[nx][ny] = dist[x][y] + 1
                queue.append((nx, ny))

    return dist


# ---------------------------------------------------------------------------
# Rankings
# ---------------------------------------------------------------------------

def _update_rankings(game_state, bfs_dist):
    """Recompute and store the current race leaderboard in game_state.rankings.

    Cars that have already finished appear first (in their finish order).
    Active cars are then sorted by BFS distance (smaller = closer to finish).
    Eliminated cars that never finished appear last.

    The result is written to game_state.rankings as a list of car IDs.
    """
    # Cars that already crossed the finish line keep their established order.
    finished_ids = list(game_state.winners)

    # Active cars: not yet finished and not eliminated.
    active_entries = []
    for car in game_state.cars:
        if car.id in game_state.winners:
            continue
        if car.eliminated:
            continue
        x, y = car.pos.x, car.pos.y
        d = -1
        if 0 <= x <= game_state.track.width and 0 <= y <= game_state.track.height:
            d = bfs_dist[x][y]
        active_entries.append((d, car.id))

    # Sort ascending by BFS distance; -1 (unreachable) sorts to the end.
    active_entries.sort(key=lambda entry: (entry[0] == -1, entry[0]))

    # Eliminated cars that never finished.
    eliminated_ids = []
    for car in game_state.cars:
        if car.eliminated and car.id not in game_state.winners:
            eliminated_ids.append(car.id)

    game_state.rankings = (
        finished_ids
        + [car_id for _, car_id in active_entries]
        + eliminated_ids
    )


# ---------------------------------------------------------------------------
# Main race loop
# ---------------------------------------------------------------------------

def run_race(game_state, renderer=None, stepwise=False):
    """Run one complete race.

    Parameters
    ----------
    game_state : GameState
        The fully initialised game state (track + cars already set up).
    renderer : Renderer or None
        When given, the renderer draws each frame and handles user input.
        When None the race runs without any window or graphics library.
    stepwise : bool
        When True (and renderer is not None), pause after every completed
        round until the user presses SPACE.

    The function returns when the race finishes or the renderer window
    is closed by the user.
    """
    controller = Controller(game_state)

    # Give the renderer a reference so it can query targets for drawing.
    if renderer is not None:
        renderer.bind_controller(controller)

    # Pre-compute the BFS distance map once — the track never changes mid-race.
    bfs_dist = _compute_bfs_dist(game_state.track)

    # Compute the initial rankings before the first move.
    _update_rankings(game_state, bfs_dist)

    running = True
    current_round = game_state.race_round  # Track round to detect boundaries.

    while running:
        # In GUI mode, collect window events first (quit, key presses, clicks).
        if renderer is not None:
            quit_requested = renderer.process_events()
            if quit_requested:
                running = False
                break

        controller.update()

        # Refresh the leaderboard after every move.
        _update_rankings(game_state, bfs_dist)

        if renderer is not None:
            renderer.render()
            renderer.tick()

        # Stepwise mode: when a new round has started, pause until SPACE.
        if stepwise and renderer is not None and not game_state.finished:
            if game_state.race_round != current_round:
                current_round = game_state.race_round
                renderer.stepwise_pause = True
                while renderer.stepwise_pause and running:
                    quit_requested = renderer.process_events()
                    if quit_requested:
                        running = False
                        break
                    renderer.render()
                    renderer.tick()

        # In headless mode the only exit condition is the race finishing.
        if renderer is None and game_state.finished:
            running = False

    if renderer is not None:
        renderer.shutdown()
