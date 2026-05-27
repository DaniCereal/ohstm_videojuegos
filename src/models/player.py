from models.character import Character

from constants import (
    RIGHT_FACING,
    LEFT_FACING
)

import arcade
from pathlib import Path


SPRITE_ROOT = Path(__file__).resolve().parents[2] / "assets" / "Sprites"

ANIMATION_FRAME_TIME = {
    "idle": 0.22,
    "walk": 0.12,
    "jump": 0.12,
    "fall": 0.07,
    "dash": 0.08,
}


class PlayerCharacter(Character):

    def __init__(self):

        super().__init__(
        )

        self.animations = {
            "idle": self.load_animation("Estatico", "Estatico"),
            "walk": self.load_animation("Movimiento", "Movimiento"),
            "jump": self.load_animation("Salto", "Salto"),
            "fall": self.load_animation("Caida", "Caida"),
            "dash": self.load_animation("Dash", "Dash"),
        }

        self.current_animation = "idle"
        self.animation_timer = 0
        self.texture = self.animations[self.current_animation][0][RIGHT_FACING]

        self.scale = 1.6

        self.climbing = False
        self.jump_pressed = False
        self.coyote_timer = 0
        self.jump_lock_timer = 0

        self.has_double_jump = False
        self.double_jump_available = False
        self.double_jump_used = False

        self.has_dash = False
        self.dash_available = False
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0
        self.dash_input_lock_timer = 0

        self.has_wall_jump = False
        self.wall_sliding = False
        self.wall_jump_lock_timer = 0
        self.wall_jump_active = False

    def load_animation(self, folder, file_prefix):
        frames_path = SPRITE_ROOT / folder
        frame_paths = sorted(
            frames_path.glob(f"{file_prefix}_*.png"),
            key=self.frame_number,
        )

        if not frame_paths:
            raise FileNotFoundError(
                f"No se encontraron sprites en {frames_path}"
            )

        animation = []
        for frame_path in frame_paths:
            texture = arcade.load_texture(str(frame_path))
            animation.append(
                (
                    texture,
                    texture.flip_left_right()
                )
            )

        return animation

    @staticmethod
    def frame_number(path):
        try:
            return (0, int(path.stem.split("_")[-1]))
        except ValueError:
            return (1, path.name)

    def get_animation_state(self):
        if self.is_dashing:
            return "dash"

        if self.wall_sliding or self.change_y < -0.1:
            return "fall"

        if self.change_y > 0.1:
            return "jump"

        if abs(self.change_x) > 0.1:
            return "walk"

        return "idle"

    def update_animation(self, delta_time):
        if (
            self.change_x < 0
            and self.facing_direction == RIGHT_FACING
        ):
            self.facing_direction = LEFT_FACING

        elif (
            self.change_x > 0
            and self.facing_direction == LEFT_FACING
        ):
            self.facing_direction = RIGHT_FACING

        animation_state = self.get_animation_state()

        if animation_state != self.current_animation:
            self.current_animation = animation_state
            self.cur_texture = 0
            self.animation_timer = 0

        frames = self.animations[self.current_animation]

        if len(frames) > 1:
            self.animation_timer += delta_time
            frame_time = ANIMATION_FRAME_TIME[self.current_animation]

            while self.animation_timer >= frame_time:
                self.cur_texture = (self.cur_texture + 1) % len(frames)
                self.animation_timer -= frame_time

        self.texture = frames[self.cur_texture][self.facing_direction]
