import pygame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Constants
SPRITE_FOLDER_ROUTE = '../sprites/'


class VisualObject(object):  # Class for the visuallity of the object

    def __init__(self, sprite_name, colorkey, x, y, object_id, is_particle, facing_right):
        super().__init__()
        self.image = pygame.image.load(SPRITE_FOLDER_ROUTE + sprite_name).convert()
        self.image.set_colorkey(colorkey)
        self.sprite_name = sprite_name
        self.colorkey = colorkey
        if not facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        self.x = x
        self.y = y
        self.state = ''
        self.moving_frame_num = 0
        self.facing_right = facing_right
        self.is_particle = is_particle

        self.object_id = object_id
        # End __init__

    def get_pos(self):  # Returns the position of the object
        return int(self.x), int(self.y)
        # End get_pos

    def update_pos(self, x, y):  # Updates the position of the object
        self.x = x
        self.y = y
        # End update_pos

    def correct_facing(self, facing):  # Function for correcting the side that the player is looking
        if self.facing_right != facing:
            self.image = pygame.transform.flip(self.image, True, False)
            self.facing_right = facing
        # End correct_facing

    def update_state(self, state):  # updates the state of the player
        self.state = state
        # End update_state

    def correct_state(self):  # A function that will change the image on the player according to his state (animation)
        if self.state == 'moving':
            if self.moving_frame_num == 3:
                self.moving_frame_num = 0
            self.image = pygame.image.load(
                SPRITE_FOLDER_ROUTE + self.sprite_name + self.state + self.moving_frame_num).convert()
            self.image.set_colorkey(self.colorkey)
            self.moving_frame_num += 1
        else:
            self.image = pygame.image.load(SPRITE_FOLDER_ROUTE + self.sprite_name + self.state).convert()
            self.image.set_colorkey(self.colorkey)
            self.moving_frame_num = 0
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        # End correct_state
