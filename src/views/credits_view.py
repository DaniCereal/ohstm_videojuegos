import arcade
from pathlib import Path

from data.settings import SETTINGS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_ROOT = PROJECT_ROOT / "assets"
LOGO_HEIGHT = 160


class CreditsView(arcade.View):
    """
    Vista de creditos con scroll vertical estilo pelicula.
    """

    def __init__(self, previous_view, music_player=None, use_main_menu=False):
        super().__init__()
        self.previous_view = previous_view
        self.music = arcade.load_sound(str(ASSETS_ROOT / "Music" / "OST" / "MusicaCreditos.ogg"))
        self.music_player = None
        self._handoff_player = music_player  # pre-playing credits track (good ending)
        self._fade_music = True              # False when music is already at full volume
        self._use_main_menu = use_main_menu  # ESC goes to MainMenu instead of previous_view
        self.fade_duration = 1.4
        self.fade_elapsed = 0
        self.fading_in = False
        self.returning_to_menu = False

        self.scroll_speed = 55
        self.line_spacing = 48
        self.top_margin = 120
        self.font_name = "Georgia"
        self.ink = (10, 14, 24)
        self.bone = (246, 239, 216)
        self.gold = (199, 150, 69)
        self.sky = (132, 190, 213)
        self.underworld = (176, 63, 45)
        self.scroll_offset = 0
        self.scroll_finished = False

        self.logo_game = arcade.load_texture(str(ASSETS_ROOT / "images" / "LogoNoBackground.png"))
        try:
            self.logo_uah = arcade.load_texture(str(ASSETS_ROOT / "images" / "LogoUAH.png"))
        except Exception:
            self.logo_uah = None

        self.credits_text = [
            ("OH HERMES SEND THE MESSAGE", "title"),
            ("", "space"),
            ("Un juego de mitologia griega", "subtitle"),
            ("", "space"),
            ("", "space"),
            ("DESARROLLO", "section"),
            ("Programador y Jefe de proyecto: Daniel Silva Moratilla", "normal"),
            ("Disenador: Brayan Cotoara Moya", "normal"),
            ("Disenador: Luis Azana Soriano", "normal"),
            ("Artista: Daniel Cordos Iloie", "normal"),
            ("", "space"),
            ("DISENO DE NIVELES", "section"),
            ("Brayan Cotoara Moya", "normal"),
            ("Luis Azana Soriano", "normal"),
            ("", "space"),
            ("MUSICA Y SONIDO", "section"),
            ("Director: Daniel Cordos Iloie", "normal"),
            ("Composicion: Suno AI", "normal"),
            ("Edicion de audio: Audacity", "normal"),
            ("Efectos de sonido: Suno AI y Daniel Silva", "normal"),
            ("", "space"),
            ("ARTE Y GRAFICOS", "section"),
            ("Sprites de personajes: Brayan Cotoara Moya", "normal"),
            ("Diseno de interfaz: Daniel Silva Moratilla", "normal"),
            ("Diseno de interfaz: Daniel Cordos Iloie", "normal"),
            ("", "space"),
            ("HERRAMIENTAS Y TECNOLOGIAS", "section"),
            ("Motor: Python Arcade Library 3.x", "normal"),
            ("Lenguaje: Python 3.12", "normal"),
            ("Editor de mapas: Tiled Map Editor", "normal"),
            ("Control de versiones: Git & GitHub", "normal"),
            ("IDE: Visual Studio Code", "normal"),
            ("", "space"),
            ("AGRADECIMIENTOS", "section"),
            ("Tutorial base: arcade.academy", "normal"),
            ("Comunidad Python Gaming", "normal"),
            ("Familia y amigos por el apoyo", "normal"),
            ("", "space"),
            ("AGRADECIMIENTOS ESPECIALES", "section"),
            ("David F Barrero", "normal"),
            ("Por su tutoria y apoyo durante el desarrollo", "small"),
            ("", "space"),
            ("CONTEXTO ACADEMICO", "section"),
            ("Universidad de Alcala", "normal"),
            ("Grado en Tecnologia de Videojuegos", "normal"),
            ("Proyecto de la asignatura de Videojuegos", "normal"),
            ("Curso academico 2025 - 2026", "normal"),
            ("", "space"),
            ("", "space"),
            ("Version: 1.0.0", "small"),
            ("2026 Oh Hermes Send The Message", "small"),
            ("Todos los derechos reservados", "small"),
            ("", "space"),
            ("", "space"),
            ("FIN DE LOS CREDITOS", "final"),
            ("", "space"),
            ("", "space"),
            ("", "space"),
            ("game", "logo"),
            ("", "space"),
            ("uah", "logo"),
            ("", "space"),
            ("", "space"),
        ]

        self.total_scroll_height = self._calculate_total_height()

    def _calculate_total_height(self):
        total = 0
        for line, style in self.credits_text:
            if style == "logo":
                total += LOGO_HEIGHT
            elif line == "":
                total += self.line_spacing * 0.75
            else:
                total += self.line_spacing
        return total

    def _line_style(self, style):
        if style == "title":
            return self.bone, 40, True
        if style == "subtitle":
            return (210, 190, 145), 22, False
        if style == "section":
            return self.sky, 30, True
        if style == "final":
            return self.gold, 34, True
        if style == "small":
            return (210, 190, 145), 20, False
        return self.bone, 24, False

    def on_show_view(self):
        arcade.camera.Camera2D().use()
        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)
        self.scroll_offset = 0
        self.scroll_finished = False
        self.fade_elapsed = 0
        self.fading_in = True
        self.returning_to_menu = False

        if self._handoff_player is not None:
            # Good ending: credits music already playing — take ownership, skip crossfade
            self.music_player = self._handoff_player
            self._handoff_player = None
            self.music_player.volume = SETTINGS.music_volume
            self._pause_previous_music()
            self._fade_music = False
        else:
            # Normal path or bad ending: start credits music and crossfade
            self._set_previous_volume(SETTINGS.music_volume)
            self.music_player = self.music.play(volume=0, loop=True)
            self._fade_music = True

    def on_draw(self):
        self.clear()

        width = self.window.width
        height = self.window.height

        self._draw_background(width, height)

        start_y = -self.top_margin + self.scroll_offset
        current_y = start_y

        for line, style in self.credits_text:
            if line == "":
                current_y -= self.line_spacing * 0.75
                continue

            if style == "logo":
                if -LOGO_HEIGHT <= current_y <= height + LOGO_HEIGHT:
                    logo_tex = self.logo_game if line == "game" else self.logo_uah
                    if logo_tex:
                        scale = min(LOGO_HEIGHT / logo_tex.height, (width * 0.45) / logo_tex.width)
                        draw_w = logo_tex.width * scale
                        draw_h = logo_tex.height * scale
                        arcade.draw_texture_rect(
                            logo_tex,
                            arcade.LBWH(width / 2 - draw_w / 2, current_y - draw_h / 2, draw_w, draw_h),
                        )
                current_y -= LOGO_HEIGHT
                continue

            if -80 <= current_y <= height + 80:
                color, font_size, bold = self._line_style(style)
                arcade.draw_text(
                    line,
                    width / 2,
                    current_y,
                    color,
                    font_size,
                    anchor_x="center",
                    anchor_y="center",
                    font_name=self.font_name,
                    bold=bold,
                )

            current_y -= self.line_spacing

        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, 70), (10, 14, 24, 130))
        arcade.draw_text(
            "ESC PARA VOLVER",
            width / 2,
            28,
            (210, 190, 145, 125),
            16,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name,
        )

        overlay_alpha = self._transition_overlay_alpha()
        if overlay_alpha > 0:
            arcade.draw_rect_filled(
                arcade.LBWH(0, 0, width, height),
                (0, 0, 0, overlay_alpha),
            )

    def _draw_background(self, width, height):
        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height), self.ink)
        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height), (0, 0, 0, 70))
        arcade.draw_rect_filled(arcade.LBWH(0, 0, width, height * 0.16), (28, 18, 22, 58))

        arcade.draw_line(80, height - 86, width - 80, height - 86, (199, 150, 69, 50), 1)
        arcade.draw_line(80, 86, width - 80, 86, (199, 150, 69, 36), 1)

    def on_update(self, delta_time):
        self._update_music_transition(delta_time)

        if self.scroll_finished:
            return

        self.scroll_offset += self.scroll_speed * delta_time

        last_line_y = -self.top_margin + self.scroll_offset - self.total_scroll_height
        if last_line_y > self.window.height + 80:
            self.scroll_finished = True

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE and not self.returning_to_menu:
            self.go_back()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.window.ctx.viewport = (0, 0, width, height)

    def _update_music_transition(self, delta_time):
        if not self.fading_in and not self.returning_to_menu:
            return

        self.fade_elapsed += delta_time
        progress = min(self.fade_elapsed / self.fade_duration, 1)
        target_volume = SETTINGS.music_volume

        if self.fading_in:
            if self._fade_music:
                self._set_previous_volume(target_volume * (1 - progress))
                self._set_credits_volume(target_volume * progress)

            if progress >= 1:
                self.fading_in = False
                if self._fade_music:
                    self._pause_previous_music()
                    self._set_credits_volume(target_volume)

        elif self.returning_to_menu:
            self._set_credits_volume(target_volume * (1 - progress))
            if not self._use_main_menu:
                self._set_previous_volume(target_volume * progress)

            if progress >= 1:
                self._stop_music()
                if self._use_main_menu:
                    from views.menu_view import MainMenu
                    self.window.show_view(MainMenu())
                else:
                    self._set_previous_volume(target_volume)
                    self.window.show_view(self.previous_view)

    def _transition_overlay_alpha(self):
        progress = min(self.fade_elapsed / self.fade_duration, 1)

        if self.fading_in:
            return int(220 * (1 - progress))
        if self.returning_to_menu:
            return int(240 * progress)
        return 0

    def _previous_player(self):
        return getattr(self.previous_view, "music_player", None)

    def _pause_previous_music(self):
        previous_player = self._previous_player()
        if previous_player is not None:
            previous_player.pause()

    def _play_previous_music(self):
        previous_player = self._previous_player()
        if previous_player is not None:
            previous_player.play()

    def _set_previous_volume(self, volume):
        previous_player = self._previous_player()
        if previous_player is not None:
            previous_player.volume = volume

    def _set_credits_volume(self, volume):
        if self.music_player is not None:
            self.music_player.volume = volume

    def _stop_music(self):
        if self.music_player is not None:
            self.music_player.pause()
            self.music_player = None

    def go_back(self):
        self.fade_elapsed = 0
        self.fading_in = False
        self.returning_to_menu = True
        if not self._use_main_menu:
            self._play_previous_music()
            self._set_previous_volume(0)
