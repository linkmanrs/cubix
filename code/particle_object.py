import pygame
from visual_object import VisualObject

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Constants
WINDOWS_WIDTH = 1100
WINDOWS_HEIGHT = 700
SPRITE_FOLDER_ROUTE = '../sprites/'
GRAVITY_CONSTANT = 10.0
T = 1 / 60  # Time constant (Uses 60 times in one second)


class Particle(object):  # Class for every particle object in the game

    def __init__(self, sprite_name, colorkey, x, y, size_x, size_y, vx, vy, gravity, object_id):
        super().__init__()
        self.object_id = object_id
        self.is_particle = True
        self.state = 'idle'
        self.x = float(x)
        self.y = float(y)
        self.size_x = size_x
        self.size_y = size_y
        self.__vx = float(vx)
        self.__vy = float(vy)
        self.__ax = 0
        self.gravity = gravity
        if self.gravity:  # Applies gravity effect
            self.__ay = GRAVITY_CONSTANT
        else:
            self.__ay = 0

        self.sprite_name = sprite_name
        self.colorkey = colorkey
        self.state = ''  # A variable for the state of the player (for the animation)
        self.facing_right = True  # Right = True
        # self.visual = VisualObject(sprite_name, colorkey, x, y)
        # End __init__

    def update_loc(self):  # Function for updating location according to speed
        self.x += self.__vx
        self.y += self.__vy
        # End update_loc

    def update_vx(self, vx):  # Function for updating speed
        self.__vx = vx
        # End update_vx

    def update_vy(self, vy):  # Function for updating speed
        self.__vy = vy
        # End update_vy

    def update_ax(self, ax):  # Function for updating acceleration
        self.__ax = ax
        # End update_ax

    def update_ay(self, ay):  # Function for updating acceleration
        self.__ay = ay
        if self.gravity:  # Applies gravity effect
            self.__ay += GRAVITY_CONSTANT
        # End update_at

    def correct_v(self):  # Function for correcting the speed according to acceleration
        self.__vx += self.__ax * T
        self.__vy += self.__ay * T
        # End correct_v

    def get_pos(self):  # Returns the position of the object
        return int(self.x), int(self.y)
        # End get_pos

    def get_v(self):  # Returns the speed of the object
        return self.__vx, self.__vy
        # End get_v

    def get_a(self):  # Returns the acceleration of the object
        return self.__ax, self.__ay
        # End get_a

    def check_facing(self):  # Check which side the player is facing
        movement = self.get_v()
        if movement[0] > 0:
            self.facing_right = True
        elif movement[0] < 0:
            self.facing_right = False
        # End check_facing
