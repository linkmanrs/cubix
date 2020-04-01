__author__ = 'Roy'

import msgpack
import socket
import pygame
from text_box import InputBox
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
RED = (200, 0, 0)
LIGHT_RED = (255, 0, 0)
GREEN = (0, 200, 0)
LIGHT_GREEN = (0, 255, 0)
BLUE = (0, 0, 200)
LIGHT_BLUE = (0, 0, 255)
GREY = (181, 181, 181)
LIGHT_GREY = (215, 215, 215)


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
        '''for visual in visual_list:
            visual.correct_state()'''
        paint_objects(screen, visual_list)

        # Refresh the screen
        pygame.display.flip()

        # Clock tick
        clock.tick(REFRESH_RATE)

        # End of main loop
    pygame.mixer.music.stop()
    # End main_visual_game


def play_theme():  # Plays the main theme of the game
    pygame.mixer.init()
    pygame.mixer.music.load(MUSIC_AND_SOUNDTRACK_ROUTE + MAIN_THEME_NAME)
    pygame.mixer.music.play(-1)
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
            'quit': True
        }

        if not finish:
            if action.get(status[0]) is not None:
                if action.get(status[0]) is True:
                    finish = True
                else:
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
            visual.update_state(status[5])
    return False
    # End update_visual


def kill_visual(status, visual_list):  # Kill the visual with the correct id
    for visual in visual_list:
        if visual.object_id == status[1]:
            visual_list.remove(visual)
    return False
    # End kill_visual


'''
status list rules:
new status = ['new', sprite_name, colorkey, x, y, object_id, is_particle]
update status = ['status', object_id, x, y, facing, state]
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


def text_objects(text, font):
    text_surface = font.render(text, True, BLACK)
    return text_surface, text_surface.get_rect()
    # End text_objects


def display_text(screen, text, x, y, large_font):  # Displays the given text on the screen
    if large_font:
        text_font = pygame.font.Font('freesansbold.ttf', 115)
    else:
        text_font = pygame.font.Font('freesansbold.ttf', 25)

    title_surf, title_rect = text_objects(text, text_font)
    title_rect.center = (x, y)
    screen.blit(title_surf, title_rect)
    # End display_text


def button(screen, message, x, y, button_width, button_height, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    activate = False

    if x + button_width > mouse[0] > x and y + button_height > mouse[1] > y:
        pygame.draw.rect(screen, active_color, (x, y, button_width, button_height))
        if click[0] == 1:
            activate = True
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, button_width, button_height))

    small_text = pygame.font.SysFont("comicsansms", 20)
    text_surf, text_rect = text_objects(message, small_text)
    text_rect.center = ((x + (button_width / 2)), (y + (button_height / 2)))
    screen.blit(text_surf, text_rect)
    return activate
    # End button


def choose_command_at_enterence(client, screen, clock):  # Let the user pick the action he wants to do
    command = ''
    while command == '':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_message('exit', client)
                return False

        screen.fill(WHITE)

        display_text(screen, "CUBIX", (WINDOWS_WIDTH / 2), (WINDOWS_HEIGHT / 2) - 50, True)

        if button(screen, "log in", 220, 500, 100, 50, GREY, LIGHT_GREY):
            command = 'log in'

        if button(screen, "sign up", 775, 500, 100, 50, GREY, LIGHT_GREY):
            command = 'sign up'

        pygame.display.flip()

        clock.tick(REFRESH_RATE)

    send_message(command, client)
    action = {
        'sign up': sign_up,
        'log in': try_log
    }
    if not action.get(command) is None:
        return action.get(command)(client, screen, clock)
    else:
        return False
    # End choose_action


def sign_up(client, screen, clock):  # Registers a user to the database

    box = InputBox(400, 500, 140, 32, False)
    response = None
    chose_name = False
    while not chose_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_message('exit', client)
                return False
            box.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if box.text != '':
                        send_message(box.text, client)
                        box.text = ''
                        box.rect.w = 140
                        response = receive_message(client)
                        if response == 'username accepted':
                            chose_name = True

        box.update()

        screen.fill(WHITE)

        display_text(screen, 'please enter your username (press enter to submit)', WINDOWS_WIDTH / 2, 200, False)

        if response is not None:
            display_text(screen, response, WINDOWS_WIDTH / 2, 300, False)

        box.draw(screen)

        pygame.display.flip()
        clock.tick(REFRESH_RATE)

    box.is_password = True
    chose_pass = False
    while not chose_pass:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_message('exit', client)
                return False
            box.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if box.text != '':
                        send_message(box.text, client)
                        box.text = ''
                        box.rect.w = 140
                        chose_pass = True

        box.update()

        screen.fill(WHITE)

        display_text(screen, 'please enter your password (press enter to submit)', WINDOWS_WIDTH / 2, 300, False)

        if response is not None:
            display_text(screen, response, WINDOWS_WIDTH / 2, 200, False)

        box.draw(screen)

        pygame.display.flip()
        clock.tick(REFRESH_RATE)

    return True
    # End register_user


def try_log(client, screen, clock):  # Trying to log in to the server
    username_box = InputBox(200, 500, 140, 32, False)
    password_box = InputBox(600, 500, 140, 32, True)
    box_list = [username_box, password_box]
    response = None
    error_message = None
    accepted = False
    denied = False
    while not accepted and not denied:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_message('exit', client)
                return False
            for box in box_list:
                box.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username_box.text != '' and password_box.text != '':
                        error_message = None
                        send_message(username_box.text, client)
                        send_message(password_box.text, client)
                        username_box.text = ''
                        username_box.rect.w = 140
                        password_box.text = ''
                        password_box.rect.w = 140
                        response = receive_message(client)
                        if response == 'user accepted':
                            accepted = True
                        elif response == 'DENIED!, too many tries were used':
                            denied = True
                    else:
                        error_message = ' at least one of the boxes is empty'

        for box in box_list:
            box.update()

        screen.fill(WHITE)

        display_text(screen, 'please enter your username and password (press enter to submit)', WINDOWS_WIDTH / 2, 200,
                     False)

        display_text(screen, 'username:', 275, 400, False)

        display_text(screen, 'password:', 675, 400, False)

        if response is not None:
            display_text(screen, response, WINDOWS_WIDTH / 2, 250, False)

        if error_message is not None:
            display_text(screen, error_message, WINDOWS_WIDTH / 2, 300, False)

        for box in box_list:
            box.draw(screen)

        pygame.display.flip()
        clock.tick(REFRESH_RATE)

    return accepted
    # End try_log


def choose_command_after_logged(client, screen, clock):  # Let the user pick the action he wants to do
    command = ''
    while command == '':
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_message('exit', client)
                return False

        screen.fill(WHITE)

        display_text(screen, "CUBIX", (WINDOWS_WIDTH / 2), (WINDOWS_HEIGHT / 2) - 50, True)

        if button(screen, "play game", 220, 500, 100, 50, GREY, LIGHT_GREY):
            command = 'play game'

        if button(screen, "get status", 775, 500, 100, 50, GREY, LIGHT_GREY):
            command = 'get status'

        pygame.display.flip()

        clock.tick(REFRESH_RATE)

    send_message(command, client)
    action = {
        'get status': get_status,
        'play game': True
    }
    if not action.get(command) is None:
        if action.get(command) is True:
            return True
        else:
            return action.get(command)(client, screen, clock)
    # End choose_action


def get_status(client, screen, clock):  # Gets the users status from the server
    message = receive_message(client)

    still_playing = False
    finish = False
    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_message('exit', client)
                return False

        screen.fill(WHITE)

        display_text(screen, message, WINDOWS_WIDTH / 2, 100, False)

        display_text(screen, 'do you still want to play the game?', (WINDOWS_WIDTH / 2), (WINDOWS_HEIGHT / 2) - 50,
                     False)

        if button(screen, "yes", 220, 450, 100, 50, GREEN, LIGHT_GREEN):
            still_playing = True
            finish = True

        if button(screen, "no", 775, 450, 100, 50, RED, LIGHT_RED):
            still_playing = False
            finish = True

        pygame.display.flip()

        clock.tick(REFRESH_RATE)

    send_message(still_playing, client)
    return still_playing
    # End get_status


def choosing_rounds(client, screen,
                    clock):  # Letting only the game ruler to choose how many rounds the players will play
    message = receive_message(client)
    rounds = None
    while rounds is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if message == 'you are the game ruler! decide how many rounds you will play':
                    send_message('exit ruler', client)
                    return False, rounds
                else:
                    send_message('exit', client)
                    return False, rounds

        screen.fill(WHITE)

        display_text(screen, message, WINDOWS_WIDTH / 2, 100, False)

        if message == 'you are the game ruler! decide how many rounds you will play':
            if button(screen, "1", 220, 350, 100, 50, GREY, LIGHT_GREY):
                rounds = 1
                send_message(rounds, client)
                return True, rounds

            if button(screen, "2", 440, 350, 100, 50, GREY, LIGHT_GREY):
                rounds = 2
                send_message(rounds, client)
                return True, rounds

            if button(screen, "3", 660, 350, 100, 50, GREY, LIGHT_GREY):
                rounds = 3
                send_message(rounds, client)
                return True, rounds

        send_message('waiting', client)
        waiting = receive_message(client)
        if waiting == 'done':
            rounds = 0

        pygame.display.flip()

        clock.tick(REFRESH_RATE)

    if message == 'you are the game ruler! decide how many rounds you will play':
        rounds = receive_message(client)
    return True, rounds
    # End choosing_rounds


def choose_character(client, screen, clock):  # A function for choosing a character
    character_list = None
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_message('exit', client)
                return False

        message = receive_message(client)
        if message != 'waiting' and message != 'done':
            character_list = message

        screen.fill(WHITE)

        sent_message = False
        if character_list is not None:
            display_text(screen, 'choose your character!', WINDOWS_WIDTH / 2, 100, False)

            pos_x = 1
            for character in character_list:
                if button(screen, character, 200 * pos_x, 450, 100, 50, GREY, LIGHT_GREY):
                    send_message(character, client)
                    character_list = None
                    sent_message = True
                pos_x += 1
        elif message == 'waiting':
            display_text(screen, 'please wait for other players', WINDOWS_WIDTH / 2, WINDOWS_HEIGHT / 2, False)

        if not sent_message and message != 'done':
            send_message('waiting', client)

        if message == 'done':
            done = True

        pygame.display.flip()

        clock.tick(REFRESH_RATE)
    return True
    # End choose_character


def create_screen(window_width, window_height):  # creates and returns the main screen
    pygame.init()
    size = (window_width, window_height)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Cubix")
    return screen
    # End create_screen


def ending_screen(message, screen, clock):  # The screen that ends the application
    finish = False
    while not finish:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True

        screen.fill(WHITE)

        display_text(screen, message, WINDOWS_WIDTH / 2, 200, False)

        display_text(screen, 'click the x to exit', WINDOWS_WIDTH / 2, 400, False)

        pygame.display.flip()

        clock.tick(REFRESH_RATE)
    # End ending_screen


def main():
    cubix_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cubix_client.connect((SERVER_IP, PORT))

    # Creating screen
    screen = create_screen(WINDOWS_WIDTH, WINDOWS_HEIGHT)
    # Adding clock
    clock = pygame.time.Clock()

    accepted = choose_command_at_enterence(cubix_client, screen, clock)
    if accepted:
        accepted = choose_command_after_logged(cubix_client, screen, clock)
        if accepted:
            accepted, num_rounds = choosing_rounds(cubix_client, screen, clock)
            if accepted:
                accepted = choose_character(cubix_client, screen, clock)
                if accepted:
                    message = receive_message(cubix_client)
                    if message == 'The game is ready':

                        while num_rounds != 0:
                            if num_rounds != 0:
                                main_visual_game(screen, clock, cubix_client)
                            num_rounds -= 1
                        winner = 'the winner is: ' + receive_message(cubix_client)
                        ending_screen(winner, screen, clock)
                    else:
                        ending_screen(message, screen, clock)
    else:
        ending_screen('come back next time! (;', screen, clock)
    cubix_client.close()
    pygame.quit()


if __name__ == '__main__':
    main()
