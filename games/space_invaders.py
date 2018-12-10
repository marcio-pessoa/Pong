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
        self.shoot_timer = Timer(200)
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
        self.ship.reset()
        self.aliens_deploy()

    def run(self):
        # Draw Space
        self.space.fill([0, 0, 0])  # Black
        # Draw objects (ship, rocks, missiles, etc...)
        self.ship.update()
        self.burst_update()
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
        formation = (6, 5)
        for y in range(formation[1]):
            for x in range(formation[0]):
                monster = Monster(self.space, y,
                                  ((self.space.get_size()[0] /
                                    formation[0]) * x +
                                   (self.space.get_size()[0] /
                                    formation[0]) / 3,
                                   ((self.space.get_size()[1] - 100) /
                                    formation[1]) * y + 30))
                self.aliens.add(monster)

    def aliens_update(self):
        # Update position
        for i in self.aliens:
            i.update()

    def aliens_check(self):
        if len(self.aliens) == 0:
            self.reset()

    def stop(self):
        pygame.event.clear()
        self.running = False

    def shoot(self):
        # Timer
        if not self.shoot_timer.check():
            return
        # Limit burst size
        if len(self.burst) >= 2:
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
        self.ship_size = [31, 31]
        self.move_increment = 5
        self.reset()
        #  alien.add((
            #  "     ##     ",
            #  "    ####    ",
            #  "    ####    ",
            #  "    ####    ",
            #  " ########## ",
            #  "############",
            #  "############",
            #  "############",
            #  ))
        self.ship = pygame.Surface(self.ship_size, SRCALPHA)
        # self.ship.fill([50, 50, 50])  # FIXME: Remove after tests
        pygame.draw.polygon(self.ship, (200, 200, 200),
                            [(0, 30), (15, 0), (30, 30), (15, 23)], 0)
        self.radius = self.ship.get_rect().center[0]
        self.update()

    def reset(self):
        self.position = [self.screen_size[0] / 2,
                         self.screen_size[1] - self.ship_size[1]]

    def update(self):
        if self.position[0] < 0:
            self.position[0] = 0
        if self.position[0] + self.ship_size[0] > self.screen.get_size()[0]:
            self.position[0] = self.screen.get_size()[0] - self.ship_size[0]
        self.rect = self.ship.get_rect().move(self.position)
        self.screen.blit(self.ship, self.position)

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
        self.radius = 3
        size = [self.radius * 2, self.radius * 2]
        position = [self.radius, self.radius]
        self.missile = pygame.Surface(size, SRCALPHA)
        pygame.draw.circle(self.missile, (210, 210, 210), position, self.radius)
        self.position = [ship_position[0] + ship_radius - self.radius,
                         ship_position[1] + self.radius]
        self.update()

    def update(self):
        self.position[1] = self.position[1] - self.speed
        if self.position[1] < 0:
            self.out = True
        self.rect = self.missile.get_rect().move(self.position)
        self.screen.blit(self.missile, self.position)

    def is_out(self):
        return self.out

    def get_radius(self):
        return self.radius

    def get_rect(self):
        return self.rect


class Monster:
    def __init__(self, screen, aspect, position):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.position = position
        aliens = []
        # Octopus (Large Invader)
        aliens.append(((
            "    ####    ",
            " ########## ",
            "############",
            "###  ##  ###",
            "############",
            "   ##  ##   ",
            "  ## ## ##  ",
            "##        ##",
            ),(
            "    ####    ",
            " ########## ",
            "############",
            "###  ##  ###",
            "############",
            "  ###  ###  ",
            " ##  ##  ## ",
            "  ##    ##  ",
            )))
        # Crab (Medium Invader)
        aliens.append(((
            "  #      #  ",
            "   #    #   ",
            "  ########  ",
            " ## #### ## ",
            "############",
            "# ######## #",
            "# #      # #",
            "   ##  ##   ",
            ),(
            "  #      #  ",
            "#  #    #  #",
            "# ######## #",
            "### #### ###",
            "############",
            " ########## ",
            "  #      #  ",
            " #        # ",
            )))
        # Cuttlefish
        aliens.append(((
            "    ####    ",
            "   ######   ",
            "  ## ## ##  ",
            "  ########  ",
            "   ##  ##   ",
            "    ####    ",
            "   #    #   ",
            "    #  #    ",
            ), (
            "    ####    ",
            "   ######   ",
            "  ## ## ##  ",
            "  ########  ",
            "   ##  ##   ",
            "    ####    ",
            "   #    #   ",
            "    #  #    ",
            )))
        # Cuttlefish
        aliens.append(((
            "    ####    ",
            "   ######   ",
            "  ## ## ##  ",
            "  ########  ",
            "   ##  ##   ",
            "    ####    ",
            "   #    #   ",
            "    #  #    ",
            ), (
            "    ####    ",
            "   ######   ",
            "  ## ## ##  ",
            "  ########  ",
            "   ##  ##   ",
            "    ####    ",
            "   #    #   ",
            "    #  #    ",
            )))
        # Cuttlefish
        aliens.append(((
            "    ####    ",
            "   ######   ",
            "  ## ## ##  ",
            "  ########  ",
            "   ##  ##   ",
            "    ####    ",
            "   #    #   ",
            "    #  #    ",
            ), (
            "    ####    ",
            "   ######   ",
            "  ## ## ##  ",
            "  ########  ",
            "   ##  ##   ",
            "    ####    ",
            "   #    #   ",
            "    #  #    ",
            )))
        self.alien = aliens[aspect]
        self.size = [48, 32]
        self.shape = pygame.Surface(self.size, SRCALPHA)
        self.caray = 0
        self.timer = Timer(500)
        self.__draw()
        self.update()

    def __draw(self):
        x = y = 0
        p = 4
        self.color = (200, 200, 200)
        self.shape.fill([0, 0, 0])
        for row in self.alien[self.caray]:
            for col in row:
                if col == "#":
                    pygame.draw.rect(self.shape, self.color, (x, y, p, p))
                x += p
            y += p
            x = 0
        self.caray = (self.caray + 1) % 2

    def update(self):
        if self.timer.check():
            self.__draw()
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def aspect(self, alien):
        self.alien = self.aliens[alien]

    def get_rect(self):
        return self.rect


class Barrier:

    def __init__(self, screen):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        position = []
        self.barrier = pygame.Surface(size, SRCALPHA)
        self.update()

    def update(self):
        self.rect = self.barrier.get_rect()
        self.screen.blit(self.barrier, self.position)

    def get_rect(self):
        return self.rect
