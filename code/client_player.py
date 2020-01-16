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


class ClientPlayer(object):  # Player class

    def __init__(self, client_id, client_socket, client_address):
        super().__init__()
        self.can_play = False
        self.client_id = client_id
        (self.client_socket) = client_socket
        (self.client_address) = client_address
        self.player_id = None
        # End __init__

    def add_player_id(self, player_id):  # Connects the client with the player object
        self.player_id = player_id
        # End add_player_object