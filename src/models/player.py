from models.character import Character

from constants import (
    RIGHT_FACING,
    LEFT_FACING
)

import arcade

class PlayerCharacter(Character):

    def __init__(self):

        super().__init__(
        )

        static_texture = arcade.load_texture(
            "../assets/Sprites/Estatico.png"
        )

        self.texture_pair = (
            static_texture,
            static_texture.flip_left_right()
        )
        self.texture = self.texture_pair[RIGHT_FACING]

        self.scale = 1

        self.climbing = False
        self.should_update_walk = 0
        self.jump_pressed = False
        self.coyote_timer = 0

        self.has_double_jump = False
        self.double_jump_available = False

        self.has_dash = False
        self.dash_available = False
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_cooldown_timer = 0

        self.has_wall_jump = False
        self.wall_sliding = False
        self.wall_jump_lock_timer = 0

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

        self.texture = self.texture_pair[self.facing_direction]
