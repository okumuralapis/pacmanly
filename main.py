import pygame
import pytmx
import sys
import os
import csv
import random

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (500, 50)
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('Menu')
font = pygame.font.Font('data/monogram.ttf', 30)
fontb = pygame.font.Font('data/monogram.ttf', 50)
clock = pygame.time.Clock()
tiles = []
points = []
special_points = [(1, 3), (23, 3), (23, 23), (1, 23)]
cnt_points_game = 0
GHOST_ADDING__EVENT_TYPE = pygame.USEREVENT
pygame.time.set_timer(GHOST_ADDING__EVENT_TYPE, 4000)
game_over = False
max_point_value = 0

with open('data/winners.csv', 'r', newline='\n', encoding="utf8") as f:
    try:
        num = int(f.readlines()[-1].split(';')[0])
    except ValueError:
        num = 0
CNT_PLAY_TIMES = num + 1


class Game:
    def __init__(self, map, hero, cur_ghost, *ghosts):
        self.cur_ghost = cur_ghost
        self.map = map
        self.hero = hero
        self.clyde, self.blinky, self.inky, self.pinky = ghosts
        self.enemies = pygame.sprite.Group(self.clyde, self.blinky, self.inky, self.pinky)
        self.counters = [0, 0, 0, 0]
        self.V = [1, 1, 1, 1]

    def render(self):
        self.map.render()
        self.hero.render()
        for en in self.enemies:
            en.render()

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

    def move_enemy(self):
        for num, i in enumerate(self.cur_ghost, start=0):
            if self.counters[num] % self.V[num] == 0:
                i.move(*self.hero.get_position())

    def check_collide(self):
        return pygame.sprite.spritecollideany(self.hero, self.cur_ghost)

    def update_counters(self):
        for i in self.counters:
            i += 0.1


class Playground:
    def __init__(self, filename):
        self.map = pytmx.load_pygame(f'data/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth

    def render(self):
        text_cnt = fontb.render(f'{cnt_points_game:03}', True, 'white')
        delta = (text_cnt.get_width() - 32) // 2
        screen.blit(text_cnt, (32 - delta + 10, 32 - delta - 15))
        for layer in self.map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and layer.name == 'background':
                for x, y, gid, in layer:
                    tile = self.map.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * self.tile_size,
                                           y * self.tile_size))
                    else:
                        tiles.append([x, y])
            if not points:
                if isinstance(layer, pytmx.TiledTileLayer) and layer.name == 'points':
                    for x, y, gid, in layer:
                        tile = self.map.get_tile_image_by_gid(gid)

                        if tile and [x, y] not in [[0, 16], [29, 16]]:
                            screen.blit(tile, (x * self.tile_size,
                                               y * self.tile_size))

                            points.append([x, y])
            else:
                if isinstance(layer, pytmx.TiledTileLayer) and layer.name == 'points':
                    for x, y, gid, in layer:
                        tile = self.map.get_tile_image_by_gid(gid)
                        if tile and [x, y] in points:
                            screen.blit(tile, (x * self.tile_size,
                                               y * self.tile_size))

    def get_tile_id(self, position):
        if self.map.get_tile_gid(*position, 0):
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
            if self.x == 0:
                self.x = 24
            elif self.x == 24:
                self.x = 1
            self.set_position((self.x, self.y))
            self.point_eating((self.x, self.y))

    def render(self):
        delta = (self.image.get_width() - 32) // 2
        screen.blit(self.image, (self.x * 32 - delta, self.y * 32 - delta))

    def get_position(self):
        return self.x, self.y

    def point_eating(self, position):
        global cnt_points_game
        x, y = position
        if (x, y) in special_points:
            cnt_points_game += 5
            special_points.remove((x, y))
            points.remove([x, y])
        elif [x, y] in points:
            cnt_points_game += 1
            points.remove([x, y])

    def set_position(self, position):
        delta = (self.image.get_width() - 32) // 2
        self.x, self.y = position
        self.rect.x = self.x * 32 - delta
        self.rect.y = self.y * 32 - delta


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


class Blinky(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__()
        self.tile_width = self.tile_height = load_image('blinky.png').get_width()

        self.image = load_image('blinky.png')
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10
        self.x, self.y = coords

    def render(self):
        delta = (self.image.get_width() - 32) // 2
        screen.blit(self.image, (self.x * 32 - delta, self.y * 32 - delta))

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        delta = (self.image.get_width() - 32) // 2
        self.x, self.y = position
        self.rect.x = self.x * 32 - delta
        self.rect.y = self.y * 32 - delta

    def move(self, px, py):
        pr = [[-1] * 25 for _ in range(25)]
        qu = []
        qu.append((self.x, self.y))
        i = 0
        used = [[0] * 25 for _ in range(25)]
        used[self.x][self.y] = 1
        while len(qu) != i:
            now = qu[i]
            i += 1
            for j in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                tx = now[0] + j[0]
                ty = now[1] + j[1]
                if [tx, ty] in tiles:
                    if used[tx][ty] == 0:
                        qu.append((tx, ty))
                        pr[tx][ty] = now
                        used[tx][ty] = 1
                        if px == tx and py == ty:
                            break
            else:
                continue
            break
        nx = px
        ny = py
        prevx = nx
        prevy = ny
        while pr[nx][ny] != -1:
            prevx = nx
            prevy = ny
            nx, ny = pr[nx][ny]
        # print(prevx, prevy)
        self.set_position((prevx, prevy))


class Inky(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__()
        self.tile_width = self.tile_height = load_image('inky.png').get_width()

        self.image = load_image('inky.png')
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10
        self.x, self.y = coords

        # pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def render(self):
        delta = (self.image.get_width() - 32) // 2
        screen.blit(self.image, (self.x * 32 - delta, self.y * 32 - delta))

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        delta = (self.image.get_width() - 32) // 2
        self.x, self.y = position
        self.rect.x = self.x * 32 - delta
        self.rect.y = self.y * 32 - delta

    def move(self, px, py):
        pr = [[-1] * 25 for _ in range(25)]
        qu = []
        qu.append((self.x, self.y))
        i = 0
        used = [[0] * 25 for _ in range(25)]
        used[self.x][self.y] = 1
        while len(qu) != i:
            now = qu[i]
            i += 1
            for j in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                tx = now[0] + j[0]
                ty = now[1] + j[1]
                if [tx, ty] in tiles:
                    if used[tx][ty] == 0:
                        qu.append((tx, ty))
                        pr[tx][ty] = now
                        used[tx][ty] = 1
                        if px == tx and py == ty:
                            break
            else:
                continue
            break
        nx = px
        ny = py
        prevx = nx
        prevy = ny
        while pr[nx][ny] != -1:
            prevx = nx
            prevy = ny
            nx, ny = pr[nx][ny]
        # print(prevx, prevy)
        self.set_position((prevx, prevy))


class Pinky(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__()
        self.tile_width = self.tile_height = load_image('pinky.png').get_width()

        self.image = load_image('pinky.png')
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10
        self.x, self.y = coords

    def move(self, px, py):
        pr = [[-1] * 25 for _ in range(25)]
        qu = []
        qu.append((self.x, self.y))
        i = 0
        used = [[0] * 25 for _ in range(25)]
        used[self.x][self.y] = 1
        while len(qu) != i:
            now = qu[i]
            i += 1
            for j in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                tx = now[0] + j[0]
                ty = now[1] + j[1]
                if [tx, ty] in tiles:
                    if used[tx][ty] == 0:
                        qu.append((tx, ty))
                        pr[tx][ty] = now
                        used[tx][ty] = 1
                        if px == tx and py == ty:
                            break
            else:
                continue
            break
        nx = px
        ny = py
        prevx = nx
        prevy = ny
        while pr[nx][ny] != -1:
            prevx = nx
            prevy = ny
            nx, ny = pr[nx][ny]
        # print(prevx, prevy)
        self.set_position((prevx, prevy))

    def render(self):
        delta = (self.image.get_width() - 32) // 2
        screen.blit(self.image, (self.x * 32 - delta, self.y * 32 - delta))

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        delta = (self.image.get_width() - 32) // 2
        self.x, self.y = position
        self.rect.x = self.x * 32 - delta
        self.rect.y = self.y * 32 - delta


class Clyde(pygame.sprite.Sprite):
    def __init__(self, coords):
        super().__init__()
        self.tile_width = self.tile_height = load_image('clyde.png').get_width()

        self.image = load_image('clyde.png')
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10
        self.x, self.y = coords

        # pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)

    def render(self):
        delta = (self.image.get_width() - 32) // 2
        screen.blit(self.image, (self.x * 32 - delta, self.y * 32 - delta))

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        delta = (self.image.get_width() - 32) // 2
        self.x, self.y = position
        self.rect.x = self.x * 32 - delta
        self.rect.y = self.y * 32 - delta

    def move(self, px, py):
        pr = [[-1] * 25 for _ in range(25)]
        qu = []
        qu.append((self.x, self.y))
        i = 0
        used = [[0] * 25 for _ in range(25)]
        used[self.x][self.y] = 1
        while len(qu) != i:
            now = qu[i]
            i += 1
            for j in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                tx = now[0] + j[0]
                ty = now[1] + j[1]
                if [tx, ty] in tiles:
                    if used[tx][ty] == 0:
                        qu.append((tx, ty))
                        pr[tx][ty] = now
                        used[tx][ty] = 1
                        if px == tx and py == ty:
                            break
            else:
                continue
            break
        nx = px
        ny = py
        prevx = nx
        prevy = ny
        while pr[nx][ny] != -1:
            prevx = nx
            prevy = ny
            nx, ny = pr[nx][ny]
        # print(prevx, prevy)
        self.set_position((prevx, prevy))


def game_over_window():
    surf = pygame.Surface((25 * 32, 25 * 32))
    text = fontb.render('GAME OVER', True, 'black')
    if cnt_points_game > 0:
        text1 = font.render(f"you've collected {cnt_points_game} points!!!", True, 'black')
    else:
        text1 = font.render(f"you did't collect any points:(", True, 'black')
    surf.fill('white')
    surf.set_alpha(200)
    screen.blit(surf, (0, 0))
    screen.blit(text, (320, 400))
    screen.blit(text1, (280, 440))


def stop_game_window():
    surf = pygame.Surface((25 * 32, 25 * 32))
    text = fontb.render('Paused', True, 'black')
    surf.fill('white')
    surf.set_alpha(200)
    screen.blit(surf, (0, 0))
    screen.blit(text, (320, 400))


def play_window():
    global cnt_points_game, tiles, points, game_over

    ghost_pos = {'m.tmx': {'blinky_pos': (10, 13), 'inky_pos': (11, 13),
                           'clyde_pos': (12, 13), 'pinky_pos': (13, 13)},
                 'm2.tmx': {'blinky_pos': (10, 14), 'inky_pos': (11, 14),
                            'clyde_pos': (12, 14), 'pinky_pos': (13, 14)},
                 'm3.tmx': {'blinky_pos': (11, 14), 'inky_pos': (12, 14),
                            'clyde_pos': (13, 14), 'pinky_pos': (14, 14)}}
    cnt_points_game = 0
    tiles = []
    points = []
    pygame.display.set_caption('Game')
    pygame.display.set_mode((25 * 32, 25 * 32))
    maps = ['m.tmx', 'm2.tmx', 'm3.tmx']
    map_num = random.randint(0, 2)
    playground = Playground(maps[map_num])
    hero = Pacman((12, 16))
    a = Blinky(ghost_pos[maps[map_num]]['blinky_pos'])
    b = Inky(ghost_pos[maps[map_num]]['inky_pos'])
    c = Pinky(ghost_pos[maps[map_num]]['pinky_pos'])
    d = Clyde(ghost_pos[maps[map_num]]['clyde_pos'])
    all_ghosts = [d, a, b, c]
    cur_ghosts = pygame.sprite.Group()
    game = Game(playground, hero, cur_ghosts, d, a, b, c)
    running = True
    pac_rot = 'left'
    stop_window = False
    game_over = False
    play_btn = Button(load_image('Play@0.5x.png'), 340, 480, '')
    exit_btn = Button(load_image('Exit@0.5x.png'), 380, 480, '')
    restart_btn = Button(load_image('Repeat-Right@0.5x.png'), 420, 480, '')
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.checkForInput(mouse_pos):
                    stop_window = False
                if exit_btn.checkForInput(mouse_pos):
                    menu()
                if restart_btn.checkForInput(mouse_pos):
                    play_window()
            if all_ghosts and event.type == GHOST_ADDING__EVENT_TYPE:
                cur_ghosts.add(all_ghosts[0])
                all_ghosts = all_ghosts[1:]
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
                if key[pygame.K_SPACE] and not stop_window:
                    stop_window = True
        screen.fill('black')
        game.render()
        if stop_window:
            stop_game_window()
            for btns in [play_btn, exit_btn, restart_btn]:
                btns.update()
        elif game_over:
            game_over_window()
            exit_btn.update()
        else:
            hero.update(game.update_hero(), pac_rot)
            game.move_enemy()
            if game.check_collide():
                game_over = True
        pygame.display.update()
        game.update_counters()
        clock.tick(6)


def winners_window():
    pygame.display.set_caption('List of winners')
    counter = 0
    speed = 3
    finished = False
    snip = font.render('', True, 'white')
    h = 100

    with open('data/winners.csv', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        res = sorted(reader, key=lambda x: int(x['cnt']), reverse=True)
    re = [(i['player'], i['cnt']) for i in res[:6]]
    coords = [(80, 100 + h) for h in range(50, 350, 50)]

    while True:
        screen.fill('#131332')
        mouse_pos = pygame.mouse.get_pos()
        title = fontb.render('Best players', True, 'white')

        clock.tick(100)
        if counter < speed * len('Best players'):
            counter += 1
        elif counter >= speed * len('Best players'):
            finished = True
        snip = fontb.render('Best players'[0:counter // speed], True, 'white')
        screen.blit(snip, (90, 50))
        for i in range(len(re)):
            tmp = font.render(
                f'{re[i][0]}player{'.' * (20 - (len(re[i][0]) + len(re[i][1]) + len("player")))}{re[i][1]}',
                True, 'white')
            screen.blit(tmp, coords[i])
            clock.tick(100)

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
    global cnt_maps, CNT_PLAY_TIMES, game_over, max_point_value
    if game_over:
        max_point_value = max(max_point_value, cnt_points_game)
    game_over = False
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption('Menu')
    counter = 0
    speed = 3
    finished = False
    snip = font.render('', True, 'white')
    title = fontb.render('Pacman', True, 'white')
    while True:
        screen.fill('#131332')
        mouse_pos = pygame.mouse.get_pos()

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
                with open('data/winners.csv', 'a', newline='\n', encoding="utf8") as f:
                    writer = csv.DictWriter(
                        f, fieldnames=['player', 'cnt'],
                        delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerow({'player': CNT_PLAY_TIMES,
                                     'cnt': max_point_value})
                max_point_value = 0
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.checkForInput(mouse_pos):
                    play_window()
                if winners_btn.checkForInput(mouse_pos):
                    winners_window()
                if quit_btn.checkForInput(mouse_pos):
                    with open('data/winners.csv', 'a', newline='\n', encoding="utf8") as f:
                        writer = csv.DictWriter(
                            f, fieldnames=['player', 'cnt'],
                            delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
                        writer.writerow({'player': CNT_PLAY_TIMES,
                                         'cnt': max_point_value})
                    max_point_value = 0
                    terminate()
        pygame.display.update()


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    sys.exit(menu())
