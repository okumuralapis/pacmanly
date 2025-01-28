import pygame
import sys
import os

global run_game, win_screen

run_game = False
win_screen = False


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print(f'Нельзя загрузить следующий файл: {fullname}')
        print(message)
        return
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


clock = pygame.time.Clock()
FPS = 30


class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action


def load_level(filenames):
    res = []
    for filename in filenames:
        filename = "data/" + filename
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        a = list(map(lambda x: x.ljust(max_width, '.'), level_map))
        res += a
    return res


def game(screen):
    pass


def start_screen(screen, w, h):
    global win_screen, run_game
    screen.fill('#131332')
    intro_text = "Pacman"
    start_button = Button(160, 200, load_image('UI-03.png'), 0.2)
    quit_button = Button(160, 250, load_image('UI-03.png'), 0.2)
    winners_button = Button(160, 300, load_image('UI-03.png'), 0.2)
    font1 = pygame.font.Font('data/monogram.ttf', 50)
    font2 = pygame.font.Font('data/monogram.ttf', 30)
    timer = pygame.time.Clock()
    snip = font1.render('', True, 'white')
    counter = 0
    speed = 3
    finished = False
    lbl1 = font2.render('Start game', True, 'white')
    lbl2 = font2.render('quit', True, 'white')
    lbl3 = font2.render('winners', True, 'white')

    running = True
    while running:
        if quit_button.draw(screen):
            running = False
        if start_button.draw(screen):
            run_game = True
        if winners_button.draw(screen):
            win_screen = True
        timer.tick(60)
        if counter < speed * len(intro_text):
            counter += 1
        elif counter >= speed * len(intro_text):
            finished = True
        snip = font1.render(intro_text[0:counter // speed], True, 'white')
        screen.blit(snip, (180, 100))
        screen.blit(lbl1, (180, 205))
        screen.blit(lbl2, (215, 250))
        screen.blit(lbl3, (205, 305))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
    return running


def winners_screen(screen):
    screen.fill('#131332')
    font1 = pygame.font.Font('data/monogram.ttf', 50)
    font1.set_italic(1)
    lbl1 = font1.render('Best players', True, 'white')


def main():
    pygame.init()
    size = w, h = 500, 500
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('pacman')
    if start_screen(screen, w, h):
        running = True
    else:
        running = False
    if win_screen:
        winners_screen(screen)
    # hero, x, y = generate_level(level_map)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill('#6986e5')
        clock.tick(FPS)
        pygame.display.flip()
    terminate()


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    sys.exit(main())
