import pygame


COLOR_INACTIVE = (181, 181, 181)
COLOR_ACTIVE = (0, 0, 0)


class InputBox:

    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = COLOR_INACTIVE
        self.text = text
        font = pygame.font.Font(None, 32)
        self.txt_surface = font.render(text, True, self.color)
        self.active = False
        # End __init__

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:  # If the user clicked on the input_box rect
            if self.rect.collidepoint(event.pos[0], event.pos[1]):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box
            if self.active:
                self.color = COLOR_ACTIVE
            else:
                self.color = COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_DELETE:
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if event.key != pygame.K_RETURN:
                        self.text += event.unicode
                # Re-render the text.
                font = pygame.font.Font(None, 32)
                self.txt_surface = font.render(self.text, True, self.color)
        # End handle_event

    def update(self):  # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width
        # End update

    def draw(self, screen):  # draws the text box on the screen
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color, self.rect, 2)
        # End draw
