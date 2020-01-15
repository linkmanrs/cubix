__author__ = 'Roy'

import pygame
import socket
import msgpack
from client_player import ClientPlayer
from cuby import Player
from cuby_angel import PlayerGhost
from platform import Block

# Constants
WINDOWS_WIDTH = 1000
WINDOWS_HEIGHT = 700
REFRESH_RATE = 60
SPRITE_FOLDER_ROUTE = '../sprites/'
MUSIC_AND_SOUNDTRACK_ROUTE = '../music and soundtrack/'
MAIN_THEME_NAME = 'forsaken dreams by edgy.mpeg'

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def check_delete_ghost(ghost, particle_list, status_list):  # Deletes the ghost if its off screen
    if ghost.y + ghost.size_y <= 0:
        particle_list.remove(ghost)
        new_status('dead', ghost, status_list)
        print('dead for good')
    # End check_delete_ghost


def check_alive(player):  # Check if the player is alive and returns the answer
    return player.health <= 0
    # End check_alive


def death(player, player_list, object_id,
          status_list):  # Makes the player die and creates a ghost particle of the player
    print('zzz')
    pos = player.get_pos()
    ghost = PlayerGhost(pos[0] - 93, pos[1] - 53, object_id, player.image_num)
    object_id += 1
    if not player.facing_right:
        ghost.facing_right = False
    new_status('new', ghost, status_list)
    player_list.remove(player)
    new_status('dead', player, status_list)
    return ghost
    # End death


def manage_collision(player, list_of_lists):  # Manages the collision protocol
    for i in range(4):
        if i != 1:
            if player.get_v()[0] > 0:
                for sprite in list_of_lists[i]:
                    if sprite is not player:
                        v = player.prevent_overlap_x(sprite)
                        if v < player.get_v()[0]:
                            player.update_vx(v)
            elif player.get_v()[0] < 0:
                for sprite in list_of_lists[i]:
                    if sprite is not player:
                        v = player.prevent_overlap_x(sprite)
                        if v > player.get_v()[0]:
                            player.update_vx(v)
            if player.get_v()[1] > 0:
                for sprite in list_of_lists[i]:
                    if sprite is not player:
                        v = player.prevent_overlap_y(sprite)
                        if v < player.get_v()[1]:
                            player.update_vy(v)
            elif player.get_v()[1] < 0:
                for sprite in list_of_lists[i]:
                    if sprite is not player:
                        v = player.prevent_overlap_y(sprite)
                        if v > player.get_v()[1]:
                            player.update_vy(v)
    # End manage_collision


def update_players(player_list, list_of_lists,
                   object_id, status_list):  # Function that contains all the necessary updates for the player list
    for player in player_list:
        pos = player.get_pos()
        player.check_death_zone()
        if check_alive(player):
            list_of_lists[1].append(death(player, player_list, object_id, status_list))
        player.hard_fall()
        player.correct_a()
        player.correct_v()

        manage_collision(player, list_of_lists)

        player.check_facing()

        player.update_loc()
        player.sync_test_rect()
        if pos != player.get_pos():
            new_status('update', player, status_list)

    return object_id
    # End update_player


def update_particles(particle_list,
                     status_list):  # Function that contains all the necessary updates for the particle list
    for particle in particle_list:
        pos = particle.get_pos()
        particle.update_loc()
        if pos != particle.get_pos():
            new_status('update', particle, status_list)
        check_delete_ghost(particle, particle_list, status_list)
    # End update_particles


def new_status(status, sprite, status_list):  # creates a new status and adds it to the status list
    if status == 'new':
        new_status_list = ['new', sprite.sprite_name, sprite.colorkey, sprite.get_pos()[0], sprite.get_pos()[1],
                           sprite.object_id, sprite.is_particle]
        status_list.append(new_status_list)
    elif status == 'update':
        new_status_list = ['update', sprite.object_id, sprite.get_pos()[0], sprite.get_pos()[1], sprite.facing_right]
        status_list.append(new_status_list)
    elif status == 'dead':
        new_status_list = ['dead', sprite.object_id]
        status_list.append(new_status_list)
    # End new_status


def new_quit_status(status_list):  # Creates a new quit status for the clients
    new_status_list = ['quit']
    status_list.append(new_status_list)
    # End new_quit_status


def collect_clients(cubix_server):  # Collects between 2-4 clients to play the game
    client_list = []

    input_received = False
    players_expected = ''
    while not input_received:
        players_expected = input("how many players expected? (a number between 1 - 4)")
        if players_expected.isdecimal():
            players_expected = int(players_expected)
            if players_expected >= 1 and players_expected <= 4:
                input_received = True
            else:
                print('incorrect input')
        else:
            print('incorrect input')

    cubix_server.listen(players_expected)

    client_id = 0
    while client_id != players_expected:
        print("waiting for more players")
        (client_socket, client_address) = cubix_server.accept()
        new_client = ClientPlayer(client_id, client_socket, client_address)
        client_list.append(new_client)
        print("player found")
        client_id += 1

    print("all players are present")
    return client_list
    # End collect_clients


def make_players(client_list, player_list, status_list, object_id):  # Create players
    i = 0
    image_num = 0
    for client in client_list:
        player = Player(i, 0, object_id, image_num)
        client.add_player_id(object_id)
        object_id += 1
        new_status('new', player, status_list)
        player_list.append(player)
        i += 150
        image_num += 1
    return object_id
    # End make_players


def floor(block_list, object_id, status_list):  # Creates a floor with blocks
    for i in range(8):
        block = Block(100 * i, WINDOWS_HEIGHT - 100, object_id)
        object_id += 1
        new_status('new', block, status_list)
        block_list.append(block)
    return object_id


def receive_event(client):  # receives the events from the client
    length = b""
    break_loop = False
    while not break_loop:
        current_byte = client.client_socket.recv(1)
        if current_byte == b"":
            raise socket.error()
        if current_byte == b"|":
            break_loop = True
        if not break_loop:
            length += current_byte
    event_bytes = client.client_socket.recv(int(length))
    event_tuple = msgpack.unpackb(event_bytes, use_list=True, raw=False)
    event = pygame.event.Event(*event_tuple)
    return event
    # End receive_event


def send_status(status_list, client):  # sends the status list to the client
    packed_status = msgpack.packb(status_list, use_bin_type=True)
    client.client_socket.send(str(len(packed_status)).encode() + b"|" + packed_status)
    # End send_status


def main_physical_game(clock, client_list):  # Main physical game
    # id variable
    object_id = 0

    # Status list that will be sent to the client
    status_list = []

    # Lists of the game objects
    object_list = []  # [0]
    particle_list = []  # [1]
    block_list = []  # [2]
    player_list = []  # [3]
    list_of_lists = [object_list, particle_list, block_list, player_list]

    object_id = make_players(client_list, player_list, status_list, object_id)

    object_id = floor(block_list, object_id, status_list)

    # Main loop
    finish = False
    while not finish:
        for client in client_list:
            event = receive_event(client)
            if event.type == pygame.QUIT:
                new_quit_status(status_list)
                finish = True
            else:
                for player in player_list:
                    if player.object_id == client.player_id:
                        if event.type == pygame.KEYDOWN:
                            player.control_movement(player.input(event))
                        elif event.type == pygame.KEYUP:
                            player.control_stop_movement(player.input(event))

        # Main game
        object_id = update_players(player_list, list_of_lists, object_id, status_list)
        update_particles(particle_list, status_list)

        # Clock tick
        clock.tick(REFRESH_RATE)
        for client in client_list:
            send_status(status_list, client)

        status_list.clear()

        # End of main loop

    pygame.quit()
    # End main_physical_game


def main():
    cubix_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cubix_server.bind(('0.0.0.0', 6565))

    client_list = collect_clients(cubix_server)

    # Adding clock
    clock = pygame.time.Clock()

    main_physical_game(clock, client_list)

    for client in client_list:
        client.client_socket.close()
    cubix_server.close()


if __name__ == '__main__':
    main()
