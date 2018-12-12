"""
space_invaders.py

Description: Space Invaders package file

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Change log:
2018-11-25
        * Version: 0.00
        * Added: Starting a new game.
"""

import math
import pygame
from pygame.locals import *
import random
from tools.timer import Timer


class SpaceInvaders:

    def __init__(self, screen):
        self.version = '0.00'
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.space = pygame.Surface(self.screen_size,
                                    HWSURFACE | SRCALPHA, 32)
        self.space.convert_alpha()
        self.running = True
        self.pad_acceleration = 1
        self.court_side = 1
        self.ship = Ship(self.space)
        self.shoot_timer = Timer(50)
        self.march_timer = Timer(500)
        self.aliens = set()
        self.reset()

    def size_reset(self):
        # Discover new size factor
        x_factor = self.screen.get_size()[0] / self.screen_size[0]
        y_factor = self.screen.get_size()[1] / self.screen_size[1]
        self.size_set()
        self.ship.screen_reset()

    def reset(self):
        self.lives = 3
        self.burst = set()
        self.walls = set()
        self.ship.reset()
        self.walls_deploy()
        self.aliens_deploy()

    def run(self):
        # Draw Space
        self.space.fill([0, 0, 0])  # Black
        # Draw objects (ship, rocks, missiles, etc...)
        self.ship.update()
        self.burst_update()
        self.walls_update()
        self.aliens_update()
        self.check_collision()
        self.aliens_check()
        if not self.lives:
            self.reset()
        # Join everything
        self.screen.blit(self.space, [0, 0])
        return False

    def check_collision(self):
        # Missle againt alien
        for i in self.aliens:
            for j in self.burst:
                if i.get_rect().colliderect(j.get_rect()):
                    self.aliens.remove(i)
                    self.burst.remove(j)
                    return

    def burst_update(self):
        # Update position
        for i in self.burst:
            i.update()
        # Check shoot age
        for i in self.burst:
            if i.is_out():
                self.burst.remove(i)
                break

    def aliens_deploy(self):
        formation = (8, 6)
        for y in range(formation[1]):
            for x in range(formation[0]):
                monster = Monster(self.space, y,
                                  [(self.space.get_size()[0] /
                                    formation[0]) * x +
                                   (self.space.get_size()[0] /
                                    formation[0]) / 3,
                                   ((self.space.get_size()[1] /
                                    (formation[1] + 3) * y)) + 30],
                                  [200, 200, 200])
                self.aliens.add(monster)

    def aliens_update(self):
        # Update position
        for i in self.aliens:
            if self.march_timer.check():
                way = True
                i.march(way)
            i.update()

    def aliens_check(self):
        if len(self.aliens) == 0:
            self.reset()

    def walls_deploy(self):
        quantity = 4
        for i in range(quantity):
            position = (self.screen.get_size()[0] / quantity * i +
                        (self.screen.get_size()[0] / quantity / 2 - 24), 400)
            barrier = Barrier(self.space, position)
            self.walls.add(barrier)

    def walls_update(self):
        for i in self.walls:
            i.update()

    def stop(self):
        pygame.event.clear()
        self.running = False

    def shoot(self):
        # Timer
        if not self.shoot_timer.check():
            return
        # Limit burst size
        if len(self.burst) >= 1:
            return
        # Shoot!
        shoot = Missile(self.space,
                        self.ship.get_position(), self.ship.get_radius())
        self.burst.add(shoot)

    def control(self, keys):
        if K_ESCAPE in keys:
            self.stop()
        if K_RIGHT in keys:
            self.ship.move_right()
        if K_LEFT in keys:
            self.ship.move_left()
        if K_SPACE in keys or \
           K_a in keys:
            self.shoot()


class Ship:

    def __init__(self, screen):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.size = [48, 32]
        self.color = (180, 180, 240)
        sprite = (
            "            ",
            "     ##     ",
            "    ####    ",
            "   ######   ",
            " ########## ",
            "  ########  ",
            " ########## ",
            "############",
            )
        self.move_increment = 5
        self.reset()
        self.shape = pygame.Surface(self.size, SRCALPHA)
        draw(self.shape, sprite, self.color, 4)
        self.radius = self.shape.get_rect().center[0]
        self.update()

    def reset(self):
        self.position = [self.screen_size[0] / 2,
                         self.screen_size[1] - self.size[1]]

    def update(self):
        if self.position[0] < 0:
            self.position[0] = 0
        if self.position[0] + self.size[0] > self.screen.get_size()[0]:
            self.position[0] = self.screen.get_size()[0] - self.size[0]
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def move_right(self):
        self.position[0] += self.move_increment

    def move_left(self):
        self.position[0] -= self.move_increment

    def get_rect(self):
        return self.rect

    def get_radius(self):
        return self.radius

    def get_position(self):
        return self.position


class Missile:
    def __init__(self, screen, ship_position, ship_radius):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.out = False
        self.speed = 5
        # self.radius = 3
        self.size = [8, 16]
        self.color = (250, 250, 250)
        sprite = (
            "##",
            "##",
            "##",
            "##",
            )
        # size = [self.radius * 2, self.radius * 2]
        position = ship_position
        self.shape = pygame.Surface(self.size, SRCALPHA)
        draw(self.shape, sprite, self.color, 4)
        # pygame.draw.circle(self.shape, (210, 210, 210), position, self.radius)
        self.position = [ship_position[0] + ship_radius - self.size[0] / 2,
                         ship_position[1] + self.size[1] / 2]
        self.update()

    def update(self):
        self.position[1] = self.position[1] - self.speed
        if self.position[1] < 0:
            self.out = True
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def is_out(self):
        return self.out

    # def get_radius(self):
        # return self.radius

    def get_rect(self):
        return self.rect


class Monster:
    def __init__(self, screen, aspect, position, color):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.aspect = aspect % 5
        self.position = position
        self.alien = self.sprite(self.aspect)
        self.size = [48, 32]
        self.color = color
        self.shape = pygame.Surface(self.size, SRCALPHA)
        self.caray = 0
        draw(self.shape, self.alien[0], self.color, 4)
        self.update()

    def sprite(self, monster):
        aliens = []
        aliens.append(((
            "    ####    ",
            " ########## ",
            "############",
            "###  ##  ###",
            "############",
            "   ##  ##   ",
            "  ## ## ##  ",
            "##        ##",
            ), (
            "    ####    ",
            " ########## ",
            "############",
            "###  ##  ###",
            "############",
            "  ###  ###  ",
            " ##  ##  ## ",
            "  ##    ##  ",
            )))
        aliens.append(((
            "  #      #  ",
            "   #    #   ",
            "  ########  ",
            " ## #### ## ",
            "############",
            "# ######## #",
            "# #      # #",
            "   ##  ##   ",
            ), (
            "  #      #  ",
            "#  #    #  #",
            "# ######## #",
            "### #### ###",
            "############",
            " ########## ",
            "  #      #  ",
            " #        # ",
            )))
        aliens.append(((
            "    ####    ",
            " ########## ",
            "############",
            "#   ####   #",
            "############",
            "   #    #   ",
            "  # #### #  ",
            " #        # ",
            ), (
            "    ####    ",
            " ########## ",
            "############",
            "#   ####   #",
            "############",
            "   # ## #   ",
            "  #      #  ",
            "   #    #   ",
            )))
        aliens.append(((
            "  #      #  ",
            "   #    #   ",
            "  ########  ",
            " ## #### ## ",
            "### #### ###",
            "# ######## #",
            "# #      # #",
            "  ##    ##  ",
            ), (
            "  #      #  ",
            "#  #    #  #",
            "# ######## #",
            "### #### ###",
            "### #### ###",
            " ########## ",
            " # #    # # ",
            "##        ##",
            )))
        aliens.append(((
            "    #  #    ",
            "   ######  #",
            "  ## ## ## #",
            "#### ## ####",
            "# ########  ",
            "# ########  ",
            "   #    #   ",
            "  ##    #   ",
            ), (
            "    #  #    ",
            "#  ######   ",
            "# ## ## ##  ",
            "#### ## ####",
            "  ######## #",
            "  ######## #",
            "   #    #   ",
            "   #    ##  ",
            )))
        return aliens[monster]

    def update(self):
        if True:
            draw(self.shape, self.alien[self.caray], self.color, 4)
            self.caray = (self.caray + 1) % 2
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def get_rect(self):
        return self.rect


class Barrier:

    def __init__(self, screen, position):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.position = position
        self.size = [48, 32]
        self.color = (210, 210, 210)
        sprite = (
            "   ######   ",
            " ########## ",
            "############",
            "############",
            "############",
            "############",
            "############",
            "############",
            )
        self.shape = pygame.Surface(self.size, SRCALPHA)
        draw(self.shape, sprite, self.color, 4)
        self.update()

    def update(self):
        self.rect = self.shape.get_rect()
        self.screen.blit(self.shape, self.position)

    def get_rect(self):
        return self.rect


def draw(shape, sprite, color, zoom):
    x = y = 0
    z = zoom
    shape.fill((0, 0, 0))
    for row in sprite:
        for col in row:
            if col == "#":
                pygame.draw.rect(shape, color, (x, y, z, z))
            x += z
        y += z
        x = 0
