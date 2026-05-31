import arcade
from pathlib import Path
from data.settings import SETTINGS

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_GOOD_TITLE = "FINAL BUENO"
_GOOD_SUBTITLE = "El equilibrio ha sido restaurado"
_GOOD_BODY = [
    "Hermes entregó el fragmento de Ambrosía Primordial.",
    "",
    "La luz del cristal se expandió por el inframundo.",
    "Hades recuperó su poder.",
    "Las puertas del Érebo se cerraron.",
    "El flujo de almas volvió a la normalidad.",
    "",
    "Por primera vez en mucho tiempo,",
    "el mensajero de los caminos tuvo libertad",
    "para elegir su propio destino.",
    "",
    "",
    '"Eres el mensajero de los caminos."',
    "— Hades",
]

_BAD_TITLE = "FINAL MALO"
_BAD_SUBTITLE = "El inframundo ha colapsado"
_BAD_BODY = [
    "Hermes llegó al inframundo sin lo que Hades necesitaba.",
    "",
    "Sin la Ambrosía, el dios de los muertos no pudo resistir.",
    "Las puertas del Érebo se abrieron.",
    "Las almas quedaron atrapadas entre mundos.",
    "",
    "El equilibrio entre los reinos",
    "se rompió definitivamente.",
    "",
    "",
    '"No eres el primero que subestima',
    ' el peso de un mensaje."',
    "— Hades",
]

_FADE_DURATION = 1.8


class EndingView(arcade.View):
    def __init__(self, good_ending: bool, previous_view):
        super().__init__()
        self.good_ending = good_ending
        self.previous_view = previous_view

        if good_ending:
            self.bg_color = (8, 10, 18)
            self.title_color = (199, 150, 69)
            self.subtitle_color = (210, 190, 145)
            self.text_color = (230, 222, 200)
            self.quote_color = (180, 165, 130)
            self.hint_color = (210, 190, 145, 90)
            self.line_color = (199, 150, 69, 45)
            music_rel = "assets/Music/OST/MusicaCreditos.ogg"
            self.title_text = _GOOD_TITLE
            self.subtitle_text = _GOOD_SUBTITLE
            self.body_lines = _GOOD_BODY
        else:
            self.bg_color = (14, 4, 4)
            self.title_color = (180, 50, 40)
            self.subtitle_color = (160, 110, 100)
            self.text_color = (205, 185, 175)
            self.quote_color = (145, 100, 90)
            self.hint_color = (160, 110, 100, 90)
            self.line_color = (140, 40, 30, 45)
            music_rel = "assets/Music/OST/Underworld_2_clean.wav"
            self.title_text = _BAD_TITLE
            self.subtitle_text = _BAD_SUBTITLE
            self.body_lines = _BAD_BODY

        self.music = arcade.load_sound(str(PROJECT_ROOT / music_rel))
        self.music_player = None

        self.fade_elapsed = 0.0
        self.fading_in = True
        self.fading_out = False
        self.ready = False

    def on_show_view(self):
        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)
        self.fade_elapsed = 0.0
        self.fading_in = True
        self.fading_out = False
        self.ready = False
        self._pause_previous_music()
        self.music_player = self.music.play(volume=SETTINGS.music_volume, loop=True)

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.window.ctx.viewport = (0, 0, width, height)

    def on_draw(self):
        self.clear()
        w = self.window.width
        h = self.window.height

        arcade.draw_rect_filled(arcade.LBWH(0, 0, w, h), self.bg_color)

        arcade.draw_line(80, h - 105, w - 80, h - 105, self.line_color, 1)
        arcade.draw_line(80, 72, w - 80, 72, self.line_color, 1)

        arcade.draw_text(
            self.title_text,
            w / 2, h - 135,
            self.title_color, 44,
            anchor_x="center", anchor_y="center",
            font_name="Georgia", bold=True,
        )
        arcade.draw_text(
            self.subtitle_text,
            w / 2, h - 188,
            self.subtitle_color, 21,
            anchor_x="center", anchor_y="center",
            font_name="Georgia",
        )

        # Body text flows downward from below the subtitle
        y = h - 232
        for line in self.body_lines:
            if line == "":
                y -= 14
                continue
            is_quote = line.startswith('"') or line.startswith(" ") or line.startswith("—")
            color = self.quote_color if is_quote else self.text_color
            size = 19 if is_quote else 22
            arcade.draw_text(
                line, w / 2, y,
                color, size,
                anchor_x="center", anchor_y="center",
                font_name="Georgia",
            )
            y -= 34

        if self.ready:
            arcade.draw_text(
                "PRESIONA CUALQUIER TECLA PARA CONTINUAR",
                w / 2, 44,
                self.hint_color, 15,
                anchor_x="center", anchor_y="center",
                font_name="Georgia",
            )

        alpha = self._overlay_alpha()
        if alpha > 0:
            arcade.draw_rect_filled(arcade.LBWH(0, 0, w, h), (0, 0, 0, alpha))

    def on_update(self, delta_time):
        if not (self.fading_in or self.fading_out):
            return
        self.fade_elapsed += delta_time
        if self.fade_elapsed >= _FADE_DURATION:
            if self.fading_in:
                self.fading_in = False
                self.ready = True
            elif self.fading_out:
                self._go_to_next()

    def _overlay_alpha(self):
        progress = min(self.fade_elapsed / _FADE_DURATION, 1.0)
        if self.fading_in:
            return int(255 * (1.0 - progress))
        if self.fading_out:
            return int(255 * progress)
        return 0

    def on_key_press(self, key, modifiers):
        if self.ready and not self.fading_out:
            self.fade_elapsed = 0.0
            self.fading_out = True
            self.ready = False

    def _go_to_next(self):
        from views.credits_view import CreditsView
        if self.good_ending:
            # Hand off the already-playing credits track — no restart, no gap
            player = self.music_player
            self.music_player = None
            self.window.show_view(CreditsView(self, music_player=player, use_main_menu=True))
        else:
            # Leave underworld music playing — CreditsView crossfades to credits
            self.window.show_view(CreditsView(self, use_main_menu=True))

    def _pause_previous_music(self):
        player = getattr(self.previous_view, "music_player", None)
        if player is not None:
            player.pause()

    def _stop_music(self):
        if self.music_player is not None:
            self.music_player.pause()
            self.music_player = None
