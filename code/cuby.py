from world_objects import WorldObject
import pygame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Constants
WINDOWS_WIDTH = 1000
WINDOWS_HEIGHT = 700
SPRITE_FOLDER_ROUTE = '../sprites/'
PLAYER_SPEED = 5.0
PLAYER_JUMP_POWER = 10.0

# Constants for WorldObject class
IMAGE_NAME = ['cuby.png', 'sphery.png', 'triangly.png', 'penty.png']
COLORKEY = RED
START_VX = 0
START_VY = 0
SIZE_X = 104
SIZE_Y = 100
GRAVITY = True
MAX_HEALTH = 5
'''DEFAULT_POWER = punch'''


class Player(WorldObject):  # Player class

    def __init__(self, x, y, object_id, image_num):
        super().__init__(IMAGE_NAME[image_num], COLORKEY, x, y, SIZE_X, SIZE_Y, START_VX, START_VY, GRAVITY, object_id)
        self.object_id = object_id
        self.__max_health = MAX_HEALTH
        self.health = self.__max_health
        self.image_num = image_num
        # End __init__

    def check_death_zone(self):  # kills the player if he fell from the screen
        if self.y >= WINDOWS_HEIGHT:
            self.health = 0
        # End check_death_zone

    def input(self, event):  # Returns the key that was pushed down
        return event.key
        # End input

    def control_movement(self, input):  # Making the player move according to the input
        action = {
            pygame.K_a: self.move_left,
            pygame.K_LEFT: self.move_left,
            pygame.K_d: self.move_right,
            pygame.K_RIGHT: self.move_right,
            pygame.K_SPACE: self.jump,
            pygame.K_UP: self.jump,
            pygame.K_w: self.jump
        }

        if not action.get(input) is None:
            action.get(input)()
        # End control_movement

    def control_stop_movement(self, input):  # Making the player stop moving according to the input
        action = {
            pygame.K_a: self.stop_moving_x,
            pygame.K_LEFT: self.stop_moving_x,
            pygame.K_d: self.stop_moving_x,
            pygame.K_RIGHT: self.stop_moving_x
        }

        if not action.get(input) is None:
            action.get(input)()
        # End control_stop_movement

    def move_left(self):  # Makes the player move left
        self.update_vx(-PLAYER_SPEED)
        # End move_left

    def move_right(self):  # Makes the player move right
        self.update_vx(PLAYER_SPEED)
        # End move_right

    def stop_moving_x(self):  # Makes the player stop moving on the x axis
        self.update_vx(0)
        # End stop_moving

    def jump(self):  # Makes the player jump
        if not self.is_moving_y():
            self.update_vy(-PLAYER_JUMP_POWER)
        # End jump
