import arcade

from models.character import Character
from constants import RIGHT_FACING, LEFT_FACING


def load_texture_pair(path):
    texture = arcade.load_texture(path)
    return (
        texture,
        texture.flip_left_right()
    )


class Enemy(Character):
    def __init__(self, name_folder, name_file, health):
        super().__init__()

        self.idle_texture_pair = load_texture_pair(
            f":resources:images/animated_characters/{name_folder}/{name_file}_idle.png"
        )
        self.walk_textures = [
            load_texture_pair(
                f":resources:images/animated_characters/{name_folder}/{name_file}_walk{i}.png"
            )
            for i in range(8)
        ]

        self.texture = self.idle_texture_pair[self.facing_direction]
        self.scale = 0.8
        self.health = health
        self.boundary_left = 0
        self.boundary_right = 0
        self.change_x = 1
        self.should_update_walk = 0

    def update_animation(self, delta_time):
        # Figure out the direction the character is facing based on the
        # movement and previous direction.
        if self.change_x < 0 and self.facing_direction == RIGHT_FACING:
            self.facing_direction = LEFT_FACING
        elif self.change_x > 0 and self.facing_direction == LEFT_FACING:
            self.facing_direction = RIGHT_FACING

        # Handle idle animations
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.facing_direction]
            return

        # Handle walking
        if self.should_update_walk == 3:
            self.cur_texture += 1
            self.cur_texture %= len(self.walk_textures)
            self.texture = self.walk_textures[self.cur_texture][self.facing_direction]
            self.should_update_walk = 0
            return

        self.should_update_walk += 1


class RobotEnemy(Enemy):
    def __init__(self):
        super().__init__("robot", "robot", health=100)


class ZombieEnemy(Enemy):
    def __init__(self):
        super().__init__("zombie", "zombie", health=50)


