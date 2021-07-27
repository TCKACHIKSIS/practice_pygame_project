import pygame
import sys
import os
import random

pygame.init()


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
            'grass2': (load_image('tile_sets/forest_tile_set/forest_grass2.png'), '*')
        }


def load_level_data(level):
    if level == 1:
        f = open("data_leveling/level1.txt", "r")
        need_data = {}
        for row in f:
            need_data[row.split()[0]] = row.split()[1]
        return need_data


class Tile():
    def __init__(self, name, image, code_sym, pos_x, pos_y):
        self.name = image
        self.image = image
        self.code_sym = code_sym
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(16 * pos_x, 16 * pos_y)


screen = pygame.display.set_mode((1000, 640))
user_data = load_user_data()
data_tileset = load_tileset_data(int(user_data['level']))
empty_tileset = []
for key in data_tileset.keys():
    empty_tileset.append(Tile(key, data_tileset[key][0], data_tileset[key][1], 0, 0))
level_stats = load_level_data(1)
map_level_template_empty = [['0'] * int(level_stats['width']) for i in range(int(level_stats['length']))]


for row in map_level_template_empty:
    for i in range(len(row)):
        seed = random.randrange(1, 3, 1)
        if seed == 1:
            row[i] = '*'
        else:
            row[i] = '#'

map_level_tile_empty = []
for i in range(len(map_level_template_empty)):
    ptr_list = []
    for j in range(len(map_level_template_empty[i])):
        if map_level_template_empty[i][j] == '#':
            ptr_list.append(Tile(empty_tileset[0].name, empty_tileset[0].image, empty_tileset[0].code_sym, i, j))
        else:
            ptr_list.append(Tile(empty_tileset[1].name, empty_tileset[1].image, empty_tileset[1].code_sym, i, j))
    map_level_tile_empty.append(ptr_list)


class Player():
    def __init__(self, image, pos_x, pos_y):
        self.image = image
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rect = self.image.get_rect().move(pos_x*16, pos_y*16)
        self.health = 10


player = Player(load_image('player/mario5.png'), 0, 20)
player.image = pygame.transform.scale(player.image, (16, 32))
health_image = load_image("player/heart pixel art 16x16.png")
for i in range(len(map_level_tile_empty)):
    for j in range(len(map_level_tile_empty[i])):
        screen.blit(map_level_tile_empty[i][j].image, map_level_tile_empty[i][j].rect)
screen.blit(player.image, player.rect)
pygame.display.flip()

while True:
    for i in range(player.health):
        screen.blit(health_image, (32 + 32*i, 16))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                player.health -= 1
                for i in range(len(map_level_tile_empty)):
                    for j in range(len(map_level_tile_empty[i])):
                        screen.blit(map_level_tile_empty[i][j].image, map_level_tile_empty[i][j].rect)
                screen.blit(player.image, player.rect)
            if event.key == pygame.K_w:
                
    pygame.display.flip()