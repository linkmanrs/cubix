from particle_object import Particle
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

# Constants for WorldObject class
IMAGE_NAME = ['cuby_angel.png', 'sphery_angel.png', 'triangly_angel.png', 'penty_angel.png']
COLORKEY = RED
START_VX = 0
START_VY = -2
SIZE_X = 291
SIZE_Y = 154
GRAVITY = False


class PlayerGhost(Particle):  # Players angel ghost particle class

    def __init__(self, x, y, object_id, image_num):
        super().__init__(IMAGE_NAME[image_num], COLORKEY, x, y, SIZE_X, SIZE_Y, START_VX, START_VY, GRAVITY, object_id)
        self.image_num = image_num
        # End __init__
