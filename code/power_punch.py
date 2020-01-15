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

# Constants for WorldObject class
IMAGE_NAME = 'punch.png'
COLORKEY = RED
START_VX = 0
START_VY = 0
SIZE_X = 50
SIZE_Y = 50
GRAVITY = False


class Punch(WorldObject):  # Punch class

    def __init__(self, x, y):
        super().__init__(IMAGE_NAME, COLORKEY, x, y, SIZE_X, SIZE_Y, START_VX, START_VY, GRAVITY)
        self.facing_right = True  # Right = True
        self.rect_facing_right = True  # Right = True
        # End __init__
