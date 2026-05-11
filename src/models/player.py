from models.character import Character

from constants import (
    RIGHT_FACING,
    LEFT_FACING
)


class PlayerCharacter(Character):

    def __init__(self):

        super().__init__(
            "female_adventurer",
            "femaleAdventurer"
        )

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

        if self.climbing and abs(self.change_y) > 1:

            self.cur_texture += 1

            if self.cur_texture > 7:
                self.cur_texture = 0

        if self.climbing:

            self.texture = self.climbing_textures[
                self.cur_texture // 4
            ]

            return

        if self.change_y > 0 and not self.climbing:

            self.texture = self.jump_texture_pair[
                self.facing_direction
            ]

            return

        elif self.change_y < 0 and not self.climbing:

            self.texture = self.fall_texture_pair[
                self.facing_direction
            ]

            return

        if self.change_x == 0:

            self.texture = self.idle_texture_pair[
                self.facing_direction
            ]

            return

        if self.should_update_walk == 3:

            self.cur_texture += 1

            if self.cur_texture > 7:
                self.cur_texture = 0

            self.texture = self.walk_textures[
                self.cur_texture
            ][self.facing_direction]

            self.should_update_walk = 0

            return

        self.should_update_walk += 1