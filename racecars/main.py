"""Main entry point for the racecars game.

This file wires together setup, track generation, driver loading, and the
game loop. In GUI mode the loop runs inside a pygame window (via Renderer).
In headless mode (--headless) no graphics library is loaded at all — the
race is driven by simulation.runner directly.
"""

import logging
import os
import random
import time
from typing import List
from simulation.game_state import GameState, Car, Track
from ui.params import GameParams
from simulation.manual_auto import MouseAuto
from simulation.script_loader import (
    load_scripts_from_folder,
    load_auto_class,
    load_track_generators_from_folder,
)
from simulation.track_runner import build_track_from_generator
from simulation.performance import PerformanceTracker
from simulation.controller import get_race_result_rows
from simulation.runner import run_race
from ui.config import (
    parse_console_args,
    parse_controllers_text,
    print_basic_console_help,
    print_advanced_console_help
)
from ui.logging_utils import setup_logging, sanitize_logger_name

# ui.renderer, ui.setup_dialog, ui.controller_dialog are imported later,
# inside _run_with_gui(), so that importing main.py never loads pygame
# when running in headless mode.

_LOGGER = logging.getLogger("racecars.main")


def _find_track_generator(generator_infos, generator_id):
    """Return the track generator that matches generator_id, or the first one.

    Matching is case-insensitive and tries the generator's internal id, its
    display name, and the source file stem — so ``--track snake``,
    ``--track Snake``, and ``--track 2_snake`` all resolve to the same generator.
    Falls back to the first available generator when no match is found, and
    returns None when the list is empty.
    """
    if generator_id is not None:
        needle = generator_id.lower()

        # Pass 1: exact id match (META["id"])
        for info in generator_infos:
            if info.id.lower() == needle:
                return info

        # Pass 2: display name match (META["name"])
        for info in generator_infos:
            if info.name.lower() == needle:
                return info

        # Pass 3: file name match (e.g. "2_snake" or "rectangular_zigzag")
        for info in generator_infos:
            file_stem = info.file_name
            dot = file_stem.rfind(".")
            if dot > 0:
                file_stem = file_stem[:dot]
            if file_stem.lower() == needle:
                return info

        _LOGGER.warning("Track generator '%s' not found. Using first available.", generator_id)
    if len(generator_infos) > 0:
        return generator_infos[0]
    return None


def _filter_visible_scripts(script_infos):
    """Remove internal/hidden scripts (e.g. RandomAuto) from the public list.

    Hidden scripts are still loaded and can be referenced by name on the CLI,
    but they are not shown in setup dialogs or used as defaults.
    """
    visible = []
    for info in script_infos:
        if info.name is None or info.name.lower() != "randomauto":
            visible.append(info)
    return visible

def _find_script_info(script_infos, name: str):
    """Look up a script by name, file name, or file name without the .py extension.

    Returns the matching ScriptInfo, or None if no match is found.
    """
    if name is None:
        return None
    target = name.lower()
    target_no_ext = _strip_py_extension(target)
    for info in script_infos:
        info_name = info.name.lower()
        info_file = info.file_name.lower()
        if info_name == target or info_file == target or info_name == target_no_ext:
            return info
    return None


def _strip_py_extension(name: str) -> str:
    """Remove a trailing '.py' suffix from a file name string, if present."""
    if name.endswith(".py"):
        return name[:-3]
    return name


def _create_cars_for_track(track: Track, players: int, controllers, script_infos) -> List[Car]:
    """Create and return the list of Car objects for one race.

    Each car gets a random name, a start position (chosen from the track's
    start vertices in a random order), and a driver — either a MouseAuto for
    human players or an auto-script loaded from the Scripts folder.

    The time spent constructing each AI driver is stored on ``car.init_ms``
    so it can be reported in the results when ``--measure`` is active.

    Parameters
    ----------
    track : Track
        The generated track; provides start positions.
    players : int
        How many cars to create (capped by available start positions).
    controllers : list[str]
        One entry per car: a script name or ``"mouse"`` for human control.
    script_infos : list[ScriptInfo]
        All loaded script descriptors (used to look up AI classes by name).
    """
    # Start order is randomized so scripts do not always get the same starting slot.
    start_positions = list(track.start_vertices)
    random.shuffle(start_positions)

    count = players
    if count > len(start_positions):
        count = len(start_positions)

    # generate random names
    ADJECTIVES = ["Red", "Blue", "Green", "Yellow", "Silver", "Black",
    "Swift", "Brave", "Wild", "Mighty", "Fierce", "Lucky"]
    NOUNS = ["Comet", "Falcon", "Tiger", "Eagle", "Rocket", "Panther",
    "Wolf", "Viper", "Storm", "Blaze", "Arrow", "Bolt"]
    random.shuffle(ADJECTIVES)
    random.shuffle(NOUNS)
    names = []
    for i in range(count):
        names.append(ADJECTIVES[i] + " " + NOUNS[i])

    cars: List[Car] = []
    for index in range(count):
        controller_name = "mouse"
        if index < len(controllers):
            controller_name = controllers[index]

        driver = MouseAuto()
        init_elapsed_ms = 0.0  # Will be overwritten for AI drivers below.
        logger = logging.getLogger("racecars.car." + sanitize_logger_name("Mouse") + ".id_" + str(index + 1))
        if controller_name.lower() != "mouse":
            try:
                script_info = _find_script_info(script_infos, controller_name)
                if script_info is None:
                    raise ValueError("Controller '%s' was not found. Falling back to mouse for car %s." % (controller_name, index + 1))
                auto_class = load_auto_class(script_info)
                if auto_class is None:
                    raise ValueError("Failed to load script '%s'. Falling back to mouse for car %s." % (script_info.name, index + 1))
                _init_start = time.perf_counter()
                driver = auto_class(track)
                init_elapsed_ms = (time.perf_counter() - _init_start) * 1000
                try:
                    name = driver.GetName()
                except Exception as ex:
                    logger.exception("GetName() failed for script '%s' (%s: %s). Using script file name as fallback.", script_info.name, type(ex).__name__, ex)
                    name = script_info.name
                names[index] = name
                logger = logging.getLogger("racecars.car." + sanitize_logger_name(script_info.name) + ".id_" + str(index + 1))
            except Exception as ex:
                _LOGGER.exception("Script '%s' raised during initialization (%s: %s). Falling back to mouse for car %s.", script_info.name, type(ex).__name__, ex, index + 1)

        # Finally create the car and attach the measured init time.
        new_car = Car(index, names[index], start_positions[index], driver = driver, logger = logger)
        new_car.controller_name = controller_name
        new_car.init_ms = init_elapsed_ms
        cars.append(new_car)

    return cars


def _filter_mouse_controllers_headless(controllers):
    """Remove 'mouse' entries from the controller list (headless mode only).

    Mouse control requires a window, so it is not allowed in headless mode.
    Each removed entry is logged at ERROR level to inform the user.
    Returns the filtered list.
    """
    filtered = []
    for name in controllers:
        if name.lower() == "mouse":
            _LOGGER.error(
                "Controller 'mouse' is not allowed in headless mode. "
                "This player will be removed from the race."
            )
        else:
            filtered.append(name)
    return filtered


def _print_start_instructions():
    """Print a short reminder of the most commonly used CLI options."""
    print("Players: use --players N or players=N")
    print("Measure: use --measure")
    print("Controllers: use --controllers mouse,ScriptName")
    print("Framerate: use --framerate N or framerate=N")
    print("Headless (no window): use --headless")
    print("List console params: use --list-params")


def _append_results_to_file(game_state, results_path, race_index):
    """Append tab-separated result rows for one race to the results file.

    Each row is prefixed with the race index so multiple races in a batch run
    can be distinguished when the file is opened in a spreadsheet.
    """
    rows = get_race_result_rows(game_state)
    file_obj = None
    try:
        file_obj = open(results_path, "a", encoding="utf-8")
        for row in rows:
            file_obj.write(str(race_index) + "\t" + row + "\n")
    finally:
        if file_obj is not None:
            file_obj.close()


def _run_with_gui(game_state, params, stepwise=False):
    """Create a pygame Renderer and run the race with a window."""
    # Import here so pygame is never loaded when running headless.
    from ui.renderer import Renderer
    renderer = Renderer(game_state, framerate=params.framerate)
    renderer.run(stepwise=stepwise) #TODO: stepwise flag should be passed at the beginning (also change in Renderer)


def main():
    """Entry point: parse configuration, set up the race, and run it.

    Steps performed:
    1. Parse console arguments and an optional config file.
    2. Load all AI scripts from the Scripts folder.
    3. Optionally show setup dialogs (skipped with --start or --headless).
    4. Generate a track and create cars with the chosen controllers.
    5. Run the race loop (with or without a pygame window).
    6. Append results to a file if --results was given.

    In multi-race mode (--races N) steps 4–6 repeat for each race.
    """
    # 1) Gather parameters and available scripts.
    parsed_config = parse_console_args(GameParams())
    params = parsed_config.params
    provided_any = parsed_config.provided_any
    start_without_dialog = parsed_config.start_without_dialog
    headless = parsed_config.headless
    list_params = parsed_config.list_params
    list_advanced_parameters = parsed_config.list_advanced_parameters
    controllers_text = parsed_config.controllers_text
    suppress_log = parsed_config.suppress_log
    log_path = parsed_config.log_path
    log_level = parsed_config.log_level
    races_count = parsed_config.races
    results_path = parsed_config.results_path
    stepwise = parsed_config.stepwise

    if suppress_log:
        setup_logging(log_level, to_console=False, file_path=None)
    else:
        setup_logging(log_level, to_console=True, file_path=log_path)

    if list_params:
        print_basic_console_help()
        if list_advanced_parameters:
            print("")
            print_advanced_console_help()
        return

    if list_advanced_parameters:
        print_advanced_console_help()
        return

    scripts_folder = os.path.join(os.path.dirname(__file__), "Scripts")
    scripts = load_scripts_from_folder(scripts_folder)
    visible_scripts = _filter_visible_scripts(scripts)
    script_names_all = [info.name for info in scripts]
    script_names_default = [info.name for info in visible_scripts]

    track_generators_folder = os.path.join(os.path.dirname(__file__), "track_generators")
    track_generators = load_track_generators_from_folder(track_generators_folder)

    # 2) Decide who will control each car (mouse vs script).
    controllers = parse_controllers_text(controllers_text)
    if controllers is not None and len(controllers) == 0:
        controllers = None

    if controllers is None and not provided_any and not start_without_dialog and len(script_names_default) > 0:
        params.players = len(script_names_default)
        if params.players > 10:
            params.players = 10

    if controllers is not None:
        params.players = len(controllers)

    # 3) Optionally run setup dialogs for easier classroom use (once, before the race loop).
    if not start_without_dialog:
        from ui.setup_dialog import SetupDialog
        dialog = SetupDialog(params, track_generators)
        params = dialog.run()
        if controllers is not None:
            params.players = len(controllers)

    if controllers is None:
        controllers = list(script_names_default[:10])
        controllers = list(controllers[:params.players])
        if len(controllers) < params.players:
            controllers.extend(["mouse"] * (params.players - len(controllers)))
        if not start_without_dialog:
            from ui.controller_dialog import ControllerDialog
            options = ["Mouse"] + script_names_all
            dialog = ControllerDialog(params.players, options, controllers)
            controllers = dialog.run()
            controllers = list(controllers[:params.players])
            if len(controllers) < params.players:
                controllers.extend(["mouse"] * (params.players - len(controllers)))

    # 4) In headless mode, mouse controllers are not allowed.
    if headless:
        controllers = _filter_mouse_controllers_headless(controllers)
        params.players = len(controllers)

    selected_generator = _find_track_generator(track_generators, params.track_generator_id)

    _print_start_instructions()
    if headless:
        print("Mode: headless (no window)")
    if races_count > 1:
        print("Races: " + str(races_count))

    # 5) Race loop: each iteration generates a new track, creates cars, and runs one race.
    for race_index in range(1, races_count + 1):
        if races_count > 1:
            print("")
            print("=== Race " + str(race_index) + " / " + str(races_count) + " ===")

        track = build_track_from_generator(selected_generator, params)
        cars = _create_cars_for_track(track, params.players, controllers, scripts)

        game_state = GameState(
            track=track,
            cars=cars,
            car_collision_penalty_enabled=params.car_collision_penalty_enabled,
            shuffle_turn_order_each_round=params.shuffle_turn_order_each_round,
            strict_target_check=params.strict_target_check,
            penalty_mode=params.penalty_mode,
            penalty_value=params.penalty_value,
            max_rounds=params.max_rounds
        )
        if params.measure_performance:
            perf_log_path = os.path.join(os.path.dirname(__file__), "performance_log.csv")
            game_state.performance = PerformanceTracker(len(cars), perf_log_path)

        game_state.race_start_time = time.time()

        # 6) Run the race — with or without a pygame window.
        if headless:
            run_race(game_state)
        else:
            _run_with_gui(game_state, params, stepwise=stepwise)

        # 7) After the race: append results to file if requested.
        if game_state.finished and results_path is not None:
            _append_results_to_file(game_state, results_path, race_index)


if __name__ == "__main__":
    main()
