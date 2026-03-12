"""Bridge between drivers and turn logic.

Each frame it asks the current driver for a target and applies the chosen move.
"""

import logging
import time
from simulation.game_state import GameState, Vertex
from simulation.move_generator import get_ordered_targets_and_validity
from simulation.turn_logic import TurnLogic
from simulation.script_api import build_world_state
from simulation.manual_auto import MouseAuto

_LOGGER = logging.getLogger("racecars.controller")


class Controller:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def apply_click(self, grid_x: int, grid_y: int):
        # Clicks are forwarded only to drivers that support manual targeting.
        if self.game_state.finished:
            return
        if not self.game_state.cars:
            return

        target = Vertex(grid_x, grid_y)
        car = self.game_state.cars[self.game_state.current_player_idx]
        if car.driver is None:
            car.logger.warning("Click ignored because current car has no driver.")
            return
        if hasattr(car.driver, "SetTarget"):
            car.driver.SetTarget(target)

    def update(self):
        # Core turn loop for one car: generate targets, ask driver, apply result.
        if self.game_state.finished:
            return
        if not self.game_state.cars:
            return

        car_id = self.game_state.current_player_idx
        car = self.game_state.cars[car_id]

        # Eliminated cars (fatal collision mode) are skipped without asking for a move.
        if car.eliminated:
            TurnLogic.apply_move(self.game_state, car_id, car.pos) # just stay in place and pass the turn to next car
            self._report_if_finished()
            return

        targets, validity = self.get_targets_and_validity()
        if len(targets) == 0:
            raise RuntimeError("No targets generated for current turn.", car)
        world = build_world_state(self.game_state)
        tracker = self.game_state.performance
        start_time = None
        if tracker is not None and tracker.enabled:
            start_time = time.perf_counter()
        target = None
        pickmove_failed = False
        try:
            target = car.PickMove(world, targets, validity)
            if target is None and isinstance(car.driver, MouseAuto):
                # Manual drivers can return None while waiting for a click.
                return
            if not isinstance(target, Vertex):
                raise ValueError(f"PickMove() returned an invalid target of type {type(target).__name__}.")
            if self.game_state.strict_target_check:
                if not self._target_in_generated_targets(target, targets):
                    pickmove_failed = True
                    car.logger.warning(
                        "PickMove() returned target (%s, %s), which is not in generated targets. "
                        "Strict target check is ON, applying safe fallback move.",
                        target.x,
                        target.y
                    )
        except Exception as ex:
            pickmove_failed = True
            car.logger.exception(
                "PickMove() raised an exception (%s: %s). Applying safe fallback move.",
                type(ex).__name__,
                ex
            )
        if start_time is not None:
            elapsed = time.perf_counter() - start_time
            tracker.record(car_id, elapsed)

        if pickmove_failed:
            target = self._drifting_target(car_id)

        if target is None:
            # Manual players can return None while waiting for a click.
            if self._driver_waits_for_click(car.driver):
                return

        TurnLogic.apply_move(self.game_state, car_id, target)
        self._report_if_finished()

    def get_targets_and_validity(self):
        if not self.game_state.cars:
            return [], []
        targets, validity = get_ordered_targets_and_validity(
            self.game_state,
            self.game_state.current_player_idx
        )
        if len(targets) == 0:
            print(self.game_state)
            raise RuntimeError(
                "No targets were generated for the current turn. "
                "This should be impossible and indicates a move generation bug."
            )
        return targets, validity

    def _drifting_target(self, car_id):
        # Ordered targets map ax=-1..1, ay=-1..1, so center is index 4.
        # But we generate it new, in case something is wrong with the provided list
        car = self.game_state.cars[car_id]
        return car.pos + car.vel

    def _target_in_generated_targets(self, target, targets):
        for item in targets:
            if item == target:
                return True
        return False

    def _driver_waits_for_click(self, driver) -> bool:
        if driver is None:
            return False
        return hasattr(driver, "SetTarget")

    def _report_if_finished(self):
        if not self.game_state.finished:
            if self.game_state.race_round > 500:
                _LOGGER.warning("Round limit reached (500). Forcing race end.")
                self.game_state.finished = True
            else:
                return
        tracker = self.game_state.performance
        if tracker is not None:
            tracker.report_if_ready(self.game_state.cars)
        _print_race_results(self.game_state)


def get_race_result_rows(game_state):
    """Return ordered result rows as a list of tab-separated strings (no header).

    Order: finishers sorted by finish_round / finish_t, then eliminated cars.
    """
    rows = []
    position = 1

    start_time_str = "-"
    if game_state.race_start_time is not None:
        start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(game_state.race_start_time))

    # Seřaď vítěze: primárně podle kola dokončení, sekundárně podle interpolovaného
    # okamžiku průjezdu cílem (t ∈ [0,1]) v rámci tahu, terciárně podle pořadí tahu.
    # Předpoklad: kolo probíhá simultánně — nižší t = auto projelo cílem dříve.
    sorted_winners = []
    for wid in game_state.winners:
        sorted_winners.append(wid)

    # Bubble sort — počet aut je malý, čitelnost důležitější než efektivita
    n = len(sorted_winners)
    for pass_index in range(n):
        for compare_index in range(n - 1 - pass_index):
            a_id = sorted_winners[compare_index]
            b_id = sorted_winners[compare_index + 1]
            a_car = game_state.cars[a_id]
            b_car = game_state.cars[b_id]
            a_round = a_car.finish_round
            b_round = b_car.finish_round
            if a_round is None:
                a_round = 999999
            if b_round is None:
                b_round = 999999
            a_t = a_car.finish_t
            b_t = b_car.finish_t
            if a_t is None:
                a_t = 1.0
            if b_t is None:
                b_t = 1.0
            # Prohoď, pokud a přijelo až po b (vyšší round, nebo stejné round ale vyšší t)
            swap = False
            if a_round > b_round:
                swap = True
            elif a_round == b_round and a_t > b_t:
                swap = True
            # Při stejném round i t: zachovej původní pořadí (pořadí tahu — terciární tiebreaker)
            if swap:
                sorted_winners[compare_index] = b_id
                sorted_winners[compare_index + 1] = a_id

    for car_id in sorted_winners:
        car = game_state.cars[car_id]
        distance_str = str(round(car.distance, 1))
        finish_round_str = str(car.finish_round) if car.finish_round is not None else "-"
        if car.finish_round is not None and car.finish_round > 0:
            avg_speed_str = str(round(car.distance / car.finish_round, 1))
        else:
            avg_speed_str = "-"
        row = start_time_str + "\t" + str(position) + "\t" + finish_round_str + "\t" + str(car.crashes) + "\t" + distance_str + "\t" + avg_speed_str + "\t" + car.name + "\t" + car.controller_name
        rows.append(row)
        position = position + 1

    # Pak auta vyřazená krachem (nedojela do cíle)
    for car in game_state.cars:
        if not car.eliminated:
            continue
        already_listed = False
        for winner_id in game_state.winners:
            if winner_id == car.id:
                already_listed = True
                break
        if already_listed:
            continue
        distance_str = str(round(car.distance, 1))
        if car.finish_round is not None and car.finish_round > 0:
            avg_speed_str = str(round(car.distance / car.finish_round, 1))
        else:
            avg_speed_str = "-"
        row = start_time_str + "\t" + str(position) + "\t-\t" + str(car.crashes) + "\t" + distance_str + "\t" + avg_speed_str + "\t" + car.name + "\t" + car.controller_name
        rows.append(row)
        position = position + 1

    return rows


def _print_race_results(game_state):
    print("")
    print("=== Výsledky závodu ===")
    print("Time\tPlace\tRounds\tCrashes\tDistance\tAvg.speed\tCar name\tController")
    rows = get_race_result_rows(game_state)
    for row in rows:
        print(row)
