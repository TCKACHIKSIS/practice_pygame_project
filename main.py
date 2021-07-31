import pygame
import sys
import os
import random

pygame.init()
screen = pygame.display.set_mode((640, 640))
main_font = pygame.font.SysFont('arial', 16)


def load_user_data():
    f = open("saves/current_save.txt", "r")
    data = f.read().split()
    f.close()
    return {'user': data[0], 'level': data[1]}


def load_image(name, color_key=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as messange:
        print('Cannot load messange', name)
        raise SystemExit(messange)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def load_tileset_data(level):
    if level == 1:
        return {
            'grass1': (load_image('tile_sets/forest_tile_set/forest_grass1.png'), '#'),
            'grass2': (load_image('tile_sets/forest_tile_set/forest_grass2.png'), '*'),
            'wall': (load_image('tile_sets/forest_tile_set/box.jpeg'), '|')
        }


sound_data = {}


def load_level_data(level):
    if level == 1:
        pygame.mixer.music.load('sounds/C418 - Minecraft.mp3')
        f = open("data_leveling/level1_grass.txt", "r")
        sound_data['walking'] = pygame.mixer.Sound('sounds/walking.mp3')
        sound_data['gulp'] = pygame.mixer.Sound('sounds/gulp.mp3')
        sound_data['wolf_angry'] = pygame.mixer.Sound('sounds/wolf_monster.mp3')
        sound_data['wolf_hurt'] = pygame.mixer.Sound('sounds/wolf_hurt.mp3')
        need_data = {}
        for row in f:
            need_data[row.split()[0]] = row.split()[1]
        return need_data


class Tile(pygame.sprite.Sprite):
    def __init__(self, name, image, code_sym, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.image = image
        self.code_sym = code_sym
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(16 * pos_x, 16 * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(pos_x * 16, pos_y * 16)
        self.health = 10
        self.damage = 1
        self.attacke_zone = pygame.Rect((self.rect.centerx+10, self.rect.centery-32), (32, 64))
        self.animation_run_set = []
        self.animation_attack_set = []
        self.current_run_image = 0
        self.animation_run_set.append(pygame.transform.scale(load_image('player/skeleton_data/run1.png'), (16, 32)))
        self.animation_run_set.append(pygame.transform.scale(load_image('player/skeleton_data/run2.png'), (16, 32)))
        self.animation_run_set.append(pygame.transform.scale(load_image('player/skeleton_data/run3.png'), (16, 32)))
        self.animation_run_set.append(pygame.transform.scale(load_image('player/skeleton_data/run4.png'), (16, 32)))
        self.animation_attack_set.append(
            pygame.transform.scale(load_image('player/skeleton_data/attack1.png'), (16, 32)))
        self.animation_attack_set.append(
            pygame.transform.scale(load_image('player/skeleton_data/attack2.png'), (16, 32)))
        self.animation_attack_set.append(
            pygame.transform.scale(load_image('player/skeleton_data/attack3.png'), (16, 32)))

    def canGo(self, to_x, to_y):
        if to_y == 1:
            to_y = 2
        if map_level_tile_empty[self.pos_x + to_x][self.pos_y + to_y].name == 'wall':
            return False
        else:
            return True

    def update(self, go, changes_pos):
        if go:
            if player.canGo(changes_pos[0], changes_pos[1]):
                sound_data['walking'].set_volume(0.5)
                sound_data['walking'].play()
                self.image = self.animation_run_set[self.current_run_image]
                self.current_run_image += 1
                if self.current_run_image > 3:
                    self.current_run_image = 0
                player.pos_x += changes_pos[0]
                player.pos_y += changes_pos[1]
                player.rect.x += changes_pos[0] * 16
                player.rect.y += changes_pos[1] * 16
        else:
            sound_data['walking'].stop()
            self.image = pygame.transform.scale(load_image('player/main_skeleton.png'), (16, 32))
            self.current_run_image = 0
        self.gotcha(enemy_group)

    def attack(self, attack_side):
        if attack_side == 'up':
            self.attacke_zone = pygame.Rect((self.rect.centerx-32, self.rect.y - 30), (64, 32))
        if attack_side == 'down':
            self.attacke_zone = pygame.Rect((self.rect.centerx-32, self.rect.y + 30), (64, 32))
        if attack_side == 'left':
            self.attacke_zone = pygame.Rect((self.rect.centerx - 42, self.rect.centery - 32), (32, 64))
        if attack_side == 'right':
            self.attacke_zone = pygame.Rect((self.rect.centerx + 10, self.rect.centery - 32), (32, 64))
        for enemy in enemy_group:
            if self.attacke_zone.colliderect(enemy.rect):
                enemy.take_damage(self.damage)

    def take_damage(self, damage):
        self.health -= damage

    def take_heal(self, heal):
        self.health += heal

    def boost_damage(self, plus_damage):
        self.damage += plus_damage

    def gotcha(self, enemy_gr):
        hits = pygame.sprite.spritecollide(self, enemy_gr, False)
        for hit in hits:
            self.take_damage(hit.damage)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect().move(pos_x * 16, pos_y * 16)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.health = 4
        self.damage = 1
        self.spawn_point_x = pos_x
        self.spawn_point_y = pos_y
        self.anger_zone = pygame.Rect((self.rect.centerx-100, self.rect.centery-100), (200, 200))

    def take_damage(self, damage_get):
        sound_data['wolf_hurt'].play()
        self.health -= damage_get
        if self.health == 0:
            self.kill()

    def is_insane(self):
        if self.anger_zone.colliderect(player.rect):
            return True
        else:
            return False

    def update(self):
        if self.is_insane():
            growl_or_not = random.randrange(0, 10, 1)
            if growl_or_not > 7:
                sound_data['wolf_angry'].play()
            if self.pos_x < player.pos_x:
                self.pos_x += 0.5
            if self.pos_x > player.pos_x:
                self.pos_x -= 0.5
            if self.pos_x == player.pos_x:
                self.pos_x = self.pos_x
            if self.pos_y < player.pos_y:
                self.pos_y += 0.5
            if self.pos_y > player.pos_y:
                self.pos_y -= 0.5
            if self.pos_y == player.pos_y:
                self.pos_y = self.pos_y
        else:
            if self.pos_x < self.spawn_point_x:
                self.pos_x += 0.5
            if self.pos_x > self.spawn_point_x:
                self.pos_x -= 0.5
            if self.pos_x == self.spawn_point_x:
                self.pos_x = self.pos_x
            if self.pos_y < self.spawn_point_y:
                self.pos_y += 0.5
            if self.pos_y > self.spawn_point_y:
                self.pos_y -= 0.5
            if self.pos_y == self.spawn_point_y:
                self.pos_y = self.pos_y
        self.rect = self.image.get_rect().move(self.pos_x * 16, self.pos_y * 16)
        self.anger_zone = pygame.Rect((self.rect.centerx - 100, self.rect.centery - 100), (200, 200))


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(self.pos_x * 16, self.pos_y * 16)

    def use_item(self, player):
        pass

    def update(self):
        if self.rect.colliderect(player.rect):
            return True
        else:
            return False


class DamageBox(ItemBox):
    def __init__(self, image, pos_x, pos_y):
        ItemBox.__init__(self, image, pos_x, pos_y)

    def use_item(self, player):
        sound_data['gulp'].play()
        player.damage += 1
        self.kill()


class HealBox(ItemBox):
    def __init__(self, image, pos_x, pos_y):
        ItemBox.__init__(self, image, pos_x, pos_y)

    def use_item(self, player):
        sound_data['gulp'].play()
        if player.health + 5 <= 10:
            player.health += 5
        else:
            player.health = 10
        self.kill()


class SpeedBox(ItemBox):
    def __init__(self, image, pos_x, pos_y):
        ItemBox.__init__(self, image, pos_x, pos_y)


player = Player(pygame.transform.scale(load_image('player/main_skeleton.png'), (16, 32)), 3, 20)

health_image = load_image("player/heart pixel art 16x16.png")
damage_image = load_image('player/damage_stat.png')
damage_image = pygame.transform.scale(damage_image, (25, 25))
enemy_image = pygame.transform.flip(load_image('enemy/howl.png'), True, False)

enemy_group = pygame.sprite.Group()
for i in range(3):
    enemy_group.add(Enemy(pygame.transform.scale(enemy_image, (32, 32)), 35, (i+1)*10))

items_group = pygame.sprite.Group()
items_group.add(
    DamageBox(load_image('items/damage_up.png'), 10, 10),
    HealBox(load_image('items/healt_up.png'), 12, 10),
    SpeedBox(load_image('items/speed_up.png'), 14, 10)
)

user_data = load_user_data()
data_tileset = load_tileset_data(int(user_data['level']))
source_tileset = []
for key in data_tileset.keys():
    source_tileset.append(Tile(key, data_tileset[key][0], data_tileset[key][1], 0, 0))
level_stats = load_level_data(1)
map_level_template_empty = [['0'] * int(level_stats['width']) for i in range(int(level_stats['length']))]
for row in map_level_template_empty:
    row[0] = '|'
    row[len(row) - 1] = '|'
    for i in range(len(row)):
        if row[i] != '|':
            seed = random.randrange(1, 3, 1)
            if seed == 1:
                row[i] = '*'
            else:
                row[i] = '#'
for i in range(len(map_level_template_empty[0])):
    map_level_template_empty[0][i] = '|'
for i in range(len(map_level_template_empty[len(map_level_template_empty)-1])):
    map_level_template_empty[len(map_level_template_empty)-1][i] = '|'
map_level_tile_empty = []
wall_group = pygame.sprite.Group()
for i in range(len(map_level_template_empty)):
    ptr_list = []
    for j in range(len(map_level_template_empty[i])):
        if map_level_template_empty[i][j] == '#':
            ptr_list.append(Tile(source_tileset[0].name, source_tileset[0].image, source_tileset[0].code_sym, i, j))
        if map_level_template_empty[i][j] == '*':
            ptr_list.append(Tile(source_tileset[1].name, source_tileset[1].image, source_tileset[1].code_sym, i, j))
        if map_level_template_empty[i][j] == '|':
            ptr_list.append(Tile(source_tileset[2].name, source_tileset[2].image, source_tileset[2].code_sym, i, j))
            wall_group.add(Tile(source_tileset[2].name, source_tileset[2].image, source_tileset[2].code_sym, i, j))
    map_level_tile_empty.append(ptr_list)

not_start = True

title_screen_gif = [pygame.transform.scale(load_image('data_leveling/welcom_gif/0.gif'), (640, 640)),
                    pygame.transform.scale(load_image('data_leveling/welcom_gif/1.gif'), (640, 640)),
                    pygame.transform.scale(load_image('data_leveling/welcom_gif/2.gif'), (640, 640)),
                    pygame.transform.scale(load_image('data_leveling/welcom_gif/3.gif'), (640, 640)),
                    pygame.transform.scale(load_image('data_leveling/welcom_gif/4.gif'), (640, 640)),
                    pygame.transform.scale(load_image('data_leveling/welcom_gif/5.gif'), (640, 640)),
                    pygame.transform.scale(load_image('data_leveling/welcom_gif/6.gif'), (640, 640)),
                    pygame.transform.scale(load_image('data_leveling/welcom_gif/7.gif'), (640, 640)),
                    pygame.transform.scale(load_image('data_leveling/welcom_gif/8.gif'), (640, 640)),
                    pygame.transform.scale(load_image('data_leveling/welcom_gif/9.gif'), (640, 640))
                    ]
end_screen_gif = [
    pygame.transform.scale(load_image('data_leveling/end_gif/0.gif'), (640, 640)),
    pygame.transform.scale(load_image('data_leveling/end_gif/1.gif'), (640, 640)),
    pygame.transform.scale(load_image('data_leveling/end_gif/2.gif'), (640, 640)),
    pygame.transform.scale(load_image('data_leveling/end_gif/3.gif'), (640, 640)),
    pygame.transform.scale(load_image('data_leveling/end_gif/4.gif'), (640, 640)),
    pygame.transform.scale(load_image('data_leveling/end_gif/5.gif'), (640, 640)),
    pygame.transform.scale(load_image('data_leveling/end_gif/6.gif'), (640, 640)),
    pygame.transform.scale(load_image('data_leveling/end_gif/7.gif'), (640, 640)),
    pygame.transform.scale(load_image('data_leveling/end_gif/8.gif'), (640, 640)),
    pygame.transform.scale(load_image('data_leveling/end_gif/9.gif'), (640, 640))
    ]


gif_count = 0
while not_start:
    pygame.time.Clock().tick(5)
    screen.blit(title_screen_gif[gif_count], (0, 0))
    gif_count += 1
    if gif_count > 9:
        gif_count = 0
    pygame.draw.rect(screen, (0, 0, 0), ((75, 180), (200, 100)))
    welcome_text = main_font.render(f"Welcome to beta_project", True, (255, 255, 255))
    menu_text = main_font.render(f"Press any key to start", False, (255, 255, 255))
    screen.blit(menu_text, (100, 250))
    screen.blit(welcome_text, (84, 200))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            not_start = False
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

isWalk = False
change_pos = (0, 0)
pressed_key = 0
for i in range(len(map_level_tile_empty)):
    for j in range(len(map_level_tile_empty[i])):
        screen.blit(map_level_tile_empty[i][j].image, map_level_tile_empty[i][j].rect)
screen.blit(player.image, player.rect)
pygame.display.flip()
timer = pygame.time.Clock()
pygame.mixer.music.play(-1)

while True:
    damage_stat_label = main_font.render(str(player.damage), False, (0, 0, 0))
    timer.tick(3)
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                pressed_key = event.key
                player.take_damage(1)
            if event.key == pygame.K_n:
                pressed_key = event.key
                player.take_heal(1)
            if event.key == pygame.K_d:
                print("ok")
                pressed_key = event.key
                isWalk = True
                change_pos = (1, 0)
            if event.key == pygame.K_a:
                pressed_key = event.key
                isWalk = True
                change_pos = (-1, 0)
            if event.key == pygame.K_w:
                pressed_key = event.key
                isWalk = True
                change_pos = (0, -1)
            if event.key == pygame.K_s:
                pressed_key = event.key
                isWalk = True
                change_pos = (0, 1)

            if keys[pygame.K_w] and keys[pygame.K_d]:
                isWalk = True
                change_pos = (1, -1)
            if keys[pygame.K_w] and keys[pygame.K_a]:
                isWalk = True
                change_pos = (-1, -1)
            if keys[pygame.K_s] and keys[pygame.K_d]:
                isWalk = True
                change_pos = (1, 1)
            if keys[pygame.K_s] and keys[pygame.K_a]:
                isWalk = True
                change_pos = (-1, 1)

            if event.key == pygame.K_UP:
                player.attack('up')
                pressed_key = event.key
            if event.key == pygame.K_DOWN:
                player.attack('down')
                pressed_key = event.key
            if event.key == pygame.K_LEFT:
                player.attack('left')
                pressed_key = event.key
            if event.key == pygame.K_RIGHT:
                player.attack('right')
                pressed_key = event.key
        if event.type == pygame.KEYUP and pressed_key == event.key:
            if pressed_key == pygame.K_w or pressed_key == pygame.K_a or pressed_key == pygame.K_s or pressed_key == pygame.K_d:
                isWalk = False
    player.update(isWalk, change_pos)
    for enemy in enemy_group:
        pygame.draw.rect(screen, (255, 0, 0), enemy.anger_zone, 3)
        enemy.update()
    for i in range(len(map_level_tile_empty)):
        for j in range(len(map_level_tile_empty[i])):
            screen.blit(map_level_tile_empty[i][j].image, map_level_tile_empty[i][j].rect)
    screen.blit(player.image, player.rect)

    for i in range(player.health):
        screen.blit(health_image, (32 + 32 * i, 16))
    screen.blit(damage_image, (25*16, 10))
    screen.blit(damage_stat_label, (27*16, 16))
    for item in items_group:
        if item.update():
            item.use_item(player)
    items_group.draw(screen)
    enemy_group.draw(screen)
    pygame.display.flip()

    if player.health == 0 or not enemy_group:
        not_start = True
        gif_count = 0
        restart_button = pygame.sprite.Sprite()
        restart_button.image = main_font.render("R - Начать заново", False, (255, 255, 255))
        restart_button.rect = ((250, 150), (250, 40))
        exit_button = pygame.sprite.Sprite()
        exit_button.image = main_font.render("esc -  Выйти", False, (255, 255, 255))
        exit_button.rect = ((250, 200), (250, 40))
        button_group_end_menu = pygame.sprite.Group()
        button_group_end_menu.add(exit_button, restart_button)
        while not_start:
            timer.tick(5)
            screen.blit(end_screen_gif[gif_count], (0, 0))
            pygame.draw.rect(screen, (0, 0, 0), ((230, 130), (200, 100)))
            screen.blit(restart_button.image, restart_button.rect)
            screen.blit(exit_button.image, exit_button.rect)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                    if event.key == pygame.K_r:
                        player = Player(pygame.transform.scale(load_image('player/main_skeleton.png'), (16, 32)), 3, 20)
                        enemy_group.empty()
                        for i in range(3):
                            enemy_group.add(Enemy(pygame.transform.scale(enemy_image, (32, 32)), 35, (i + 1) * 10))
                        items_group.add(
                            DamageBox(load_image('items/damage_up.png'), 10, 10),
                            HealBox(load_image('items/healt_up.png'), 12, 10),
                            SpeedBox(load_image('items/speed_up.png'), 14, 10)
                        )
                        not_start = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            gif_count += 1
            if gif_count > 9:
                gif_count = 0

            pygame.display.flip()