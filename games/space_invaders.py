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
        # Spawn monsters
        for i in range(8):
            monster = Monster(self.screen, (10 * i, i))
            self.aliens.add(monster)

    def run(self):
        # Draw Space
        self.space.fill([0, 0, 0])  # Black
        # Draw objects (ship, rocks, missiles, etc...)
        self.ship.update()
        self.burst_update()
        self.aliens_update()
        # self.check_collision()
        if not self.lives:
            self.reset()
        # Join everything
        self.screen.blit(self.space, [0, 0])
        return False

    def check_collision(self):
        for i in self.rock_group:
            # Ship against rocks
            if i.get_rect().colliderect(self.ship.get_rect()):
                self.rock_group.remove(i)
                self.lives -= 1
                return
            # Missile against rocks
            for j in self.burst:
                if j.get_rect().colliderect(i.get_rect()):
                    self.rock_group.remove(i)
                    self.burst.remove(j)
                    return
            # Rock against rocks
            for j in self.rock_group:
                if j == i:
                    continue
                if j.get_rect().colliderect(i.get_rect()):
                    i.upgrade(j.get_size())
                    self.rock_group.remove(j)
                    return

    def rock_update(self):
        # Need more?
        while len(self.rock_group) < 8:
            rock = Sprite(self.space)
            if not rock.get_rect().colliderect(self.ship.get_double_rect()):
                self.rock_group.add(rock)
        # Update position
        for i in self.rock_group:
            i.update()

    def burst_update(self):
        # Update position
        for i in self.burst:
            i.update()
        # Check shoot age
        for i in self.burst:
            if i.is_out():
                self.burst.remove(i)
                break

    def aliens_update(self):
        # Update position
        for i in self.aliens:
            i.update()

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
        self.ship = pygame.Surface(self.ship_size, SRCALPHA)
        self.ship.fill([50, 50, 50])  # FIXME: Remove after tests
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
    def __init__(self, screen, position):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.size = [31, 31]
        self.shape = pygame.Surface(self.size, SRCALPHA)
        self.shape.fill([50, 50, 50])  # FIXME: Remove after tests
        pygame.draw.rect(self.shape, (200, 200, 200),
                         (0, 0, self.size[0], self.size[1]), 20)
        self.position = position
        self.update()

    def type(self, type):
        self.type = type

    def update(self):
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

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
