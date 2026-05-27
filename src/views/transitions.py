import arcade


class FadeToView(arcade.View):
    """Fade a negro y luego muestra la siguiente vista."""

    def __init__(self, from_view, to_view_factory, duration=0.55):
        super().__init__()
        self.from_view = from_view
        self.to_view_factory = to_view_factory  # callable sin argumentos
        self.duration = duration
        self.elapsed = 0.0
        self._done = False

    def on_draw(self):
        self.from_view.on_draw()
        alpha = int(255 * min(self.elapsed / self.duration, 1.0))
        arcade.draw_rect_filled(
            arcade.LBWH(0, 0, self.window.width, self.window.height),
            (0, 0, 0, alpha),
        )

    def on_update(self, delta_time):
        if self._done:
            return
        self.elapsed += delta_time
        if self.elapsed >= self.duration:
            self._done = True
            self.window.show_view(self.to_view_factory())