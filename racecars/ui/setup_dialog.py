"""Simple setup window for game parameters before a race starts."""

import pygame
from ui.params import GameParams

class SetupDialog:
    def __init__(self, params: GameParams, generator_infos=None):
        self.params = params.clone()
        self.generator_infos = generator_infos if generator_infos is not None else []
        self.screen = None
        self.font = None
        self.clock = None
        self.fields = []
        self.active_index = 0

    def run(self) -> GameParams:
        # Modal-style loop: collect values, then return updated params.
        pygame.init()
        self.font = pygame.font.SysFont("consolas", 18)
        self.clock = pygame.time.Clock()
        self._build_fields()
        # Size window to fit all fields plus buttons.
        fields_height = 60 + len(self.fields) * 34 + 80
        if fields_height < 480:
            fields_height = 480
        self.screen = pygame.display.set_mode((640, fields_height))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse(event.pos)
                elif event.type == pygame.KEYDOWN:
                    running = self._handle_key(event.key, event.unicode)

            self._render()
            self.clock.tick(30)

        pygame.quit()
        return self.params

    def _build_fields(self):
        # Field order controls the layout and keyboard tab order.
        self.fields = [
            _Field("W (width)", "width", str(self.params.width)),
            _Field("H (height)", "height", str(self.params.height)),
            _Field("Players", "players", str(self.params.players)),
            _Field("Track width mean", "track_width_mean", str(self.params.track_width_mean)),
            _Field("Track width var", "track_width_var", str(self.params.track_width_var)),
            _Field("Turn sharpness", "turn_sharpness", str(self.params.turn_sharpness)),
            _Field("Turn density", "turn_density", str(self.params.turn_density)),
            _Field("Measure perf (0/1)", "measure", "1" if self.params.measure_performance else "0"),
            _Field("Seed (empty = random)", "seed", "" if self.params.seed is None else str(self.params.seed))
        ]

        # Add track generator selector if any generators are available.
        if len(self.generator_infos) > 0:
            initial_index = 0
            if self.params.track_generator_id is not None:
                for i in range(len(self.generator_infos)):
                    if self.generator_infos[i].id == self.params.track_generator_id:
                        initial_index = i
                        break
            self.fields.append(_SelectField("Track generator", "track_generator_id",
                                            self.generator_infos, initial_index))

    def _handle_mouse(self, pos):
        x, y = pos
        field_index = self._field_index_at(y)
        if field_index is not None:
            field = self.fields[field_index]
            if isinstance(field, _SelectField):
                # Clicking a select field cycles its option.
                field.index += 1
                if field.index >= len(field.options):
                    field.index = 0
            self.active_index = field_index
            return

        btn_y = self._buttons_y()
        if self._button_hit(x, y, 500, btn_y, 110, 40):
            self._apply_fields_to_params()
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

    def _handle_key(self, key, text):
        if key == pygame.K_ESCAPE:
            return False
        if key == pygame.K_RETURN:
            self._apply_fields_to_params()
            return False
        if key == pygame.K_TAB:
            self.active_index += 1
            if self.active_index >= len(self.fields):
                self.active_index = 0
            return True
        if key == pygame.K_BACKSPACE:
            field = self.fields[self.active_index]
            if not isinstance(field, _SelectField) and len(field.value) > 0:
                field.value = self._remove_last_char(field.value)
            return True

        if text == "":
            return True

        field = self.fields[self.active_index]
        # Select fields do not accept text input.
        if isinstance(field, _SelectField):
            return True
        if self._text_allowed(field.key, text):
            field.value = field.value + text
        return True

    def _apply_fields_to_params(self):
        # Parse validated fields back into typed GameParams values.
        for field in self.fields:
            if isinstance(field, _SelectField):
                self._apply_select_field(field)
            else:
                self._apply_field_value(field)

    def _apply_select_field(self, field):
        if field.key == "track_generator_id":
            selected = field.options[field.index]
            self.params.track_generator_id = selected.id

    def _apply_field_value(self, field):
        if field.key == "seed":
            if field.value.strip() == "":
                self.params.seed = None
                return
            if self._is_int_string(field.value, True):
                self.params.seed = int(field.value)
            return
        if field.key == "measure":
            if field.value.strip() == "1":
                self.params.measure_performance = True
            else:
                self.params.measure_performance = False
            return

        if not self._is_int_string(field.value, False):
            return

        value = int(field.value)
        if field.key == "width":
            self.params.width = value
        elif field.key == "height":
            self.params.height = value
        elif field.key == "players":
            self.params.players = value
        elif field.key == "track_width_mean":
            self.params.track_width_mean = value
        elif field.key == "track_width_var":
            self.params.track_width_var = value
        elif field.key == "turn_sharpness":
            self.params.turn_sharpness = value
        elif field.key == "turn_density":
            self.params.turn_density = value

    def _render(self):
        # Repaint whole form each frame for straightforward UI logic.
        self.screen.fill((230, 230, 230))
        title = self.font.render("Setup", True, (0, 0, 0))
        self.screen.blit(title, (20, 20))

        y = 60
        for index, field in enumerate(self.fields):
            label = self.font.render(field.label, True, (0, 0, 0))
            self.screen.blit(label, (20, y))
            box_rect = pygame.Rect(260, y - 4, 260, 26)
            color = (200, 200, 200)
            if index == self.active_index:
                color = (255, 255, 255)
            pygame.draw.rect(self.screen, color, box_rect)
            pygame.draw.rect(self.screen, (120, 120, 120), box_rect, 1)

            if isinstance(field, _SelectField):
                selected_name = field.options[field.index].name
                display_text = "< " + selected_name + " >"
                value_label = self.font.render(display_text, True, (0, 0, 120))
            else:
                value_label = self.font.render(field.value, True, (0, 0, 0))

            self.screen.blit(value_label, (265, y))
            y += 34

        btn_y = self._buttons_y()
        self._draw_button(500, btn_y, 110, 40, "Start")

        pygame.display.flip()

    def _draw_button(self, x, y, w, h, text):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, (210, 210, 210), rect)
        pygame.draw.rect(self.screen, (120, 120, 120), rect, 1)
        label = self.font.render(text, True, (0, 0, 0))
        label_x = x + (w - label.get_width()) // 2
        label_y = y + (h - label.get_height()) // 2
        self.screen.blit(label, (label_x, label_y))

    def _button_hit(self, x, y, bx, by, bw, bh):
        if x < bx or x > bx + bw:
            return False
        if y < by or y > by + bh:
            return False
        return True

    def _buttons_y(self):
        return 60 + len(self.fields) * 34 + 14

    def _field_index_at(self, y):
        top = 60
        for index in range(len(self.fields)):
            field_top = top + index * 34
            if y >= field_top - 4 and y <= field_top + 22:
                return index
        return None

    def _text_allowed(self, key: str, text: str) -> bool:
        if key == "seed":
            return text.isdigit() or text == "-" 
        return text.isdigit()

    def _is_int_string(self, text: str, allow_negative: bool) -> bool:
        if text == "":
            return False
        index = 0
        if allow_negative and text[0] == "-":
            if len(text) == 1:
                return False
            index = 1
        for ch in text[index:]:
            if not ch.isdigit():
                return False
        return True

    def _remove_last_char(self, text: str) -> str:
        if text == "":
            return text
        return text[:-1]

class _Field:
    def __init__(self, label: str, key: str, value: str):
        self.label = label
        self.key = key
        self.value = value


class _SelectField:
    def __init__(self, label: str, key: str, options, index: int):
        # options is a list of TrackGeneratorInfo objects (or any object with .name and .id).
        self.label = label
        self.key = key
        self.options = options
        self.index = index
