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

    def __init__(self, sprite_name, colorkey, x, y, object_id, is_particle):
        super().__init__()
        self.image = pygame.image.load(SPRITE_FOLDER_ROUTE + sprite_name).convert()
        self.image.set_colorkey(colorkey)
        self.sprite_name = sprite_name
        self.colorkey = colorkey

        self.x = x
        self.y = y
        self.facing_right = True
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
