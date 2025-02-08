import pygame
import pytmx
import sys
import os
import csv

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 50)
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('Menu')
font = pygame.font.Font('data/monogram.ttf', 30)
fontb = pygame.font.Font('data/monogram.ttf', 50)
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
tiles = []


class Game:
    def __init__(self, map, hero, ghosts):
        self.map = map
        self.hero = hero
        self.ghosts = ghosts

    def render(self, screen):
        self.map.render()
        # self.hero.render(screen)
        # self.ghosts.render(screen)

    def update_hero(self):
        next_x, next_y = self.hero.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if [next_x, next_y] in tiles:
            return next_x, next_y
        return


class Playground:
    def __init__(self, filename, free_tiles):
        self.map = pytmx.load_pygame(f'data/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth

    def render(self):
        for layer in self.map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name == 'background':
                for x, y, gid, in layer:
                    tile = self.map.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * self.tile_size,
                                           y * self.tile_size))
                    else:
                        tiles.append([x, y])


    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def is_free(self, position):
        return self.get_tile_id(position)


class Pacman(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__()
        self.tile_width = self.tile_height = load_image(os.path.join('pacman-left', '1.png')).get_width()

        self.rt = 'pacman-left'
        self.image = load_image(f'{self.rt}/1.png')
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10
        self.cur_frame = 0
        self.x, self.y = coords

    def update(self, new_coords, rotation, *args):
        self.rt = f'pacman-{rotation}'
        self.frames = [load_image(f'{self.rt}/1.png'),
                       load_image(f'{self.rt}/2.png'),
                       load_image(f'{self.rt}/3.png')]
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if new_coords:
            self.x, self.y = new_coords

    def render(self):
        delta = (self.image.get_width() - 32) // 2
        screen.blit(self.image, (self.x * 32 - delta, self.y * 32 - delta))

    def get_position(self):
        return self.x, self.y


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


class Button:
    def __init__(self, image, x_pos, y_pos, text_input):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_input = text_input
        self.text = font.render(self.text_input, True, "white")
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            return True

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top,
                                                                                          self.rect.bottom):
            self.text = font.render(self.text_input, True, "blue")
        else:
            self.text = font.render(self.text_input, True, "white")


class Enemy:
    pass


def play_window():
    pygame.display.set_caption('Game')
    pygame.display.set_mode((960, 1020))
    playground = Playground('m.tmx', [30, 46])
    hero = Pacman((14, 18))
    ghosts = Enemy()
    game = Game(playground, hero, ghosts)
    running = True
    game_over = False
    pac_rot = 'left'
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            key = pygame.key.get_pressed()
            if key.count(True) == 1:
                if key[pygame.K_UP]:
                    pac_rot = 'up'
                if key[pygame.K_DOWN]:
                    pac_rot = 'down'
                if key[pygame.K_RIGHT]:
                    pac_rot = 'right'
                if key[pygame.K_LEFT]:
                    pac_rot = 'left'
        screen.fill('black')
        playground.render()
        hero.update(game.update_hero(), pac_rot)
        hero.render()
        pygame.display.flip()
        clock.tick(7)


def winners_window():
    pygame.display.set_caption('List of winners')
    counter = 0
    speed = 3
    finished = False
    snip = font.render('', True, 'white')
    b = 40

    with open('data/winners.csv') as f:
        reader = csv.reader(f, delimiter=';', quotechar='"')
        re = [f'{names} {score}' for names, score in reader]

    while True:
        screen.fill('#131332')
        mouse_pos = pygame.mouse.get_pos()
        title = fontb.render('Best players', True, 'white')

        clock.tick(60)
        if counter < speed * len('Best players'):
            counter += 1
        elif counter >= speed * len('Best players'):
            finished = True
        snip = fontb.render('Best players'[0:counter // speed], True, 'white')
        screen.blit(snip, (90, 50))
        for i in re[1:]:
            tmp = font.render(i, True, 'white')
            screen.blit(tmp, (100, b))
            clock.tick(60)

        btn_pic = load_image('UI-03.png')
        btn_pic = pygame.transform.scale(btn_pic, (100, 40))
        back_btn = Button(btn_pic, 60, 30, 'Back')
        back_btn.changeColor(mouse_pos)
        back_btn.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.checkForInput(mouse_pos):
                    menu()
        pygame.display.update()


def menu():
    pygame.display.set_caption('Menu')
    counter = 0
    speed = 3
    finished = False
    snip = font.render('', True, 'white')

    while True:
        screen.fill('#131332')
        mouse_pos = pygame.mouse.get_pos()
        title = fontb.render('Pacman', True, 'white')

        clock.tick(60)
        if counter < speed * len('Pacman'):
            counter += 1
        elif counter >= speed * len('Pacman'):
            finished = True
        snip = fontb.render('Pacman'[0:counter // speed], True, 'white')
        screen.blit(snip, (140, 100))

        btn_pic = load_image('UI-03.png')
        btn_pic = pygame.transform.scale(btn_pic, (150, 40))
        play_btn = Button(btn_pic, 200, 200, 'Start game')
        winners_btn = Button(btn_pic, 200, 250, 'Winners')
        quit_btn = Button(btn_pic, 200, 300, 'Quit')

        for btns in [play_btn, quit_btn, winners_btn]:
            btns.changeColor(mouse_pos)
            btns.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.checkForInput(mouse_pos):
                    play_window()
                if winners_btn.checkForInput(mouse_pos):
                    winners_window()
                if quit_btn.checkForInput(mouse_pos):
                    terminate()
        pygame.display.update()


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    sys.exit(menu())
