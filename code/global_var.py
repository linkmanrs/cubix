class GlobalVariable:  # A class that will contain all the necessary global variable
    def __init__(self):
        self.object_id = 0
        self.star_cooldown = 0

        # Status list that will be sent to the client
        self.status_list = []

        # Lists of the game objects
        self.object_list = []  # [0]
        self.particle_list = []  # [1]
        self.block_list = []  # [2]
        self.player_list = []  # [3]
        self.power_list = []  # [4]
        self.list_of_lists = [self.object_list, self.particle_list, self.block_list, self.player_list, self.power_list]
