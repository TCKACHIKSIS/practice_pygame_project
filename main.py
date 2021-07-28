import pygame
import sys
import os
import random

pygame.init()
screen = pygame.display.set_mode((640, 640))


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


def load_level_data(level):
    if level == 1:
        f = open("data_leveling/level1_grass.txt", "r")
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
                player.pos_x += changes_pos[0]
                player.pos_y += changes_pos[1]
                player.rect.x += changes_pos[0] * 16
                player.rect.y += changes_pos[1] * 16
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
        self.anger_zone = pygame.Rect((self.rect.centerx-100, self.rect.centery-100), (200, 200))

    def take_damage(self, damage_get):
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
            self.rect = self.image.get_rect().move(self.pos_x * 16, self.pos_y * 16)
            self.anger_zone = pygame.Rect((self.rect.centerx - 100, self.rect.centery - 100), (200, 200))


player = Player(pygame.transform.scale(load_image('player/mario5.png'), (16, 32)), 3, 20)
player_group = pygame.sprite.Group()
health_image = load_image("player/heart pixel art 16x16.png")
enemy_image = pygame.transform.flip(load_image('enemy/howl.png'), True, False)
enemy_group = pygame.sprite.Group()
for i in range(3):
    enemy_group.add(Enemy(pygame.transform.scale(enemy_image, (32, 32)), 35, (i+1)*10))

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
for i in range(len(map_level_template_empty)):
    ptr_list = []
    for j in range(len(map_level_template_empty[i])):
        if map_level_template_empty[i][j] == '#':
            ptr_list.append(Tile(source_tileset[0].name, source_tileset[0].image, source_tileset[0].code_sym, i, j))
        if map_level_template_empty[i][j] == '*':
            ptr_list.append(Tile(source_tileset[1].name, source_tileset[1].image, source_tileset[1].code_sym, i, j))
        if map_level_template_empty[i][j] == '|':
            ptr_list.append(Tile(source_tileset[2].name, source_tileset[2].image, source_tileset[2].code_sym, i, j))
    map_level_tile_empty.append(ptr_list)


isWalk = False
change_pos = (0, 0)
pressed_key = 0
for i in range(len(map_level_tile_empty)):
    for j in range(len(map_level_tile_empty[i])):
        screen.blit(map_level_tile_empty[i][j].image, map_level_tile_empty[i][j].rect)
screen.blit(player.image, player.rect)
pygame.display.flip()
timer = pygame.time.Clock()
while True:
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

            if keys[pygame.K_d]:
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
            if keys[pygame.K_w] and keys[pygame.K_a]:
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
    for enemy in enemy_group:
        pygame.draw.rect(screen, (255, 0, 0), enemy.anger_zone, 3)

    if not enemy_group:
        pygame.quit()
        sys.exit()

    if player.health == 0:
        pygame.quit()
        sys.exit()


    enemy_group.draw(screen)
    pygame.display.flip()
