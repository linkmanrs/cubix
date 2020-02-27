__author__ = 'Roy'

import msgpack
import socket
import pygame
from visual_object import VisualObject

# Constants
WINDOWS_WIDTH = 1100
WINDOWS_HEIGHT = 700
REFRESH_RATE = 60
SPRITE_FOLDER_ROUTE = '../sprites/'
MUSIC_AND_SOUNDTRACK_ROUTE = '../ost/'
MAIN_THEME_NAME = 'forsaken dreams by edgy.mpeg'
SERVER_IP = '127.0.0.1'
PORT = 6565

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def main_visual_game(screen, clock, cubix_client):  # The main game with only visuals
    visual_list = []  # List of all the visual objects
    # play_theme()

    finish = False
    while not finish:
        event = pygame.event.poll()
        send_event(event, cubix_client)

        # Paints background
        screen.fill(WHITE)

        status_list = receive_status(cubix_client)

        finish = process_data(status_list, visual_list)
        paint_objects(screen, visual_list)

        # Refresh the screen
        pygame.display.flip()

        # Clock tick
        clock.tick(REFRESH_RATE)

        # End of main loop
    pygame.quit()
    # End main_visual_game


def play_theme():  # Plays the main theme of the game
    pygame.mixer.init()
    pygame.mixer.music.load(MUSIC_AND_SOUNDTRACK_ROUTE + MAIN_THEME_NAME)
    pygame.mixer.music.play()
    # End play_theme


def receive_status(cubix_client):  # receives the status list from the client
    length = b""
    break_loop = False
    while not break_loop:
        current_byte = cubix_client.recv(1)
        if current_byte == b"":
            raise socket.error()
        if current_byte == b"|":
            break_loop = True
        if not break_loop:
            length += current_byte
    status_list_bytes = cubix_client.recv(int(length))
    status_list = msgpack.unpackb(status_list_bytes, use_list=True, raw=False)
    return status_list
    # End receive_status


def receive_message(client):  # receives the events from the client
    length = b""
    break_loop = False
    while not break_loop:
        current_byte = client.recv(1)
        if current_byte == b"":
            raise socket.error()
        if current_byte == b"|":
            break_loop = True
        if not break_loop:
            length += current_byte
    message_bytes = client.recv(int(length))
    message = msgpack.unpackb(message_bytes, use_list=True, raw=False)
    return message
    # End receive_event


def send_event(event, cubix_client):  # sends the event to the client
    packed_event = msgpack.packb((event.type, event.dict), use_bin_type=True)
    cubix_client.send(str(len(packed_event)).encode() + b"|" + packed_event)
    # End send_event


def send_message(message, cubix_client):
    packed_event = msgpack.packb(message, use_bin_type=True)
    cubix_client.send(str(len(packed_event)).encode() + b"|" + packed_event)
    # End send_message


def process_data(status_list, visual_list):  # Uses the data from the server to progress the game
    finish = False
    for status in status_list:
        action = {
            'new': new_visual,
            'update': update_visual,
            'dead': kill_visual,
            'quit': quit_game
        }

        if not finish:
            finish = action.get(status[0])(status, visual_list)
    return finish
    # End process_data


def new_visual(status, visual_list):  # Create new visual object
    visual = VisualObject(status[1], status[2], status[3], status[4], status[5], status[6], status[7])
    visual_list.append(visual)
    return False
    # End new_visual


def update_visual(status, visual_list):  # Updates the visual with the correct id
    for visual in visual_list:
        if visual.object_id == status[1]:
            visual.update_pos(status[2], status[3])
            visual.correct_facing(status[4])
    return False
    # End update_visual


def kill_visual(status, visual_list):  # Kill the visual with the correct id
    for visual in visual_list:
        if visual.object_id == status[1]:
            visual_list.remove(visual)
    return False
    # End kill_visual


def quit_game(status, visual_list):  # Returns false for finish
    return True
    # End quit_game


'''
status list rules:
new status = ['new', sprite_name, colorkey, x, y, object_id, is_particle]
update status = ['status', object_id, x, y, facing]
dead status = ['dead', object_id]
quit status = ['quit']
'''


def paint_objects(screen, object_list):  # paints all the objects in the list on the screen
    for Object in object_list:
        if Object.is_particle:
            screen.blit(Object.image, Object.get_pos())
    for Object in object_list:
        if not Object.is_particle:
            screen.blit(Object.image, Object.get_pos())
    # End paint_objects


def choose_command_at_enterence(client):  # Let the user pick the action he wants to do
    print('please choose one of these actions:')
    command_list = ['log in', 'sign up']
    command = input(command_list)
    send_message(command, client)
    action = {
        'sign up': sign_up,
        'log in': try_log
    }
    if not action.get(command) is None:
        return action.get(command)(client)
    else:
        return False
    # End choose_action


def sign_up(client):  # Registers a user to the database
    chose_name = False
    while not chose_name:
        user_name = input('please enter your username')
        if user_name != '':
            send_message(str(user_name), client)
            response = receive_message(client)
            print(response)
            if response == 'username accepted':
                chose_name = True
        else:
            print('invalid user name')

    chose_pass = False
    while not chose_pass:
        password = input('please enter your password')
        if password != '':
            send_message(str(password), client)
            chose_pass = True
        else:
            print('invalid password')
    print(receive_message(client))
    return True
    # End register_user


def try_log(client):  # Trying to log in to the server
    selected_name = False
    while not selected_name:
        user_name = input('please enter your username')
        if user_name != '':
            send_message(str(user_name), client)
            response = receive_message(client)
            print(response)
            if response == 'username accepted':
                selected_name = True
        else:
            print('invalid user name')

    accepted = False
    blocked = False
    while not accepted and not blocked:
        password = input('please enter your password')
        if password != '':
            send_message(str(password), client)
            response = receive_message(client)
            print(response)
            if response == 'password accepted':
                accepted = True
            elif response == 'DENIED!, too many tries were used':
                blocked = True
        else:
            send_message('invalid password', client)

    if accepted:
        print(receive_message(client))
    return accepted
    # End try_log


def choose_character(cubix_client):  # A function for choosing a character
    chose_character = False
    character = ''
    character_list = receive_status(cubix_client)
    while not chose_character:
        print('choose your character:')
        character = input(character_list)
        if character in character_list:
            send_message(character, cubix_client)
            chose_character = True
        elif character == 'aa':
            send_message(character_list[0], cubix_client)
            chose_character = True
        else:
            print('invalid character name')
    print('character chosen: ' + str(character))
    # End choose_character


def create_screen(window_width, window_height):  # creates and returns the main screen
    pygame.init()
    size = (window_width, window_height)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Cubix")
    return screen
    # End create_screen


def main():
    cubix_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cubix_client.connect((SERVER_IP, PORT))

    accepted = choose_command_at_enterence(cubix_client)
    if accepted:
        choose_character(cubix_client)

        message = receive_message(cubix_client)
        print(message)
        if message == 'The game is ready':
            screen = create_screen(WINDOWS_WIDTH, WINDOWS_HEIGHT)

            # Adding clock
            clock = pygame.time.Clock()
            main_visual_game(screen, clock, cubix_client)

    cubix_client.close()


if __name__ == '__main__':
    main()
