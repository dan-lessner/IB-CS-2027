"""Simulation runner - drives the game loop without any graphics dependency.

The core race loop lives here so it can run both with a renderer (GUI mode)
and without one (headless mode). The renderer is an optional argument;
when it is None the race runs silently and exits as soon as it finishes.
"""

import logging
from simulation.controller import Controller

_LOGGER = logging.getLogger("racecars.runner")


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

    running = True
    current_round = game_state.race_round  # track round to detect boundaries

    while running:
        # In GUI mode, collect window events first (quit, key presses, clicks).
        if renderer is not None:
            quit_requested = renderer.process_events()
            if quit_requested:
                running = False
                break

        controller.update()

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
