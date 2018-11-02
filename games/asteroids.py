"""
asteroids.py

Description: Asteroids package file

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Change log:
2018-11-dd
        * Version: 0.02
        * Added: Pygame version.

2014-09-06
        * Version: 0.01
        * Added: First version.
"""

import math
import pygame
from pygame.locals import *
import random


class Asteroids:
    def __init__(self, screen):
        self.version = '0.02'
        self.screen = screen
        self.running = False

    def start(self):
        self.running = True
        self.size_set()
        self.pad_acceleration = 1
        self.court_side = 1
        self.reset()
        self.set()
        self.ship.start()
        self.rock.start()

    def size_set(self):
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.space = pygame.Surface(self.screen_size,
                                    HWSURFACE | SRCALPHA, 32)
        self.space.convert_alpha()

    def size_reset(self):
        # Discover new size factor
        x_factor = self.screen.get_size()[0] / self.screen_size[0]
        y_factor = self.screen.get_size()[1] / self.screen_size[1]
        self.size_set()
        self.ship.screen_reset()

    def set(self):
        self.ship = Ship(self.space)
        self.rock = Sprite(self.space)

    def reset(self):
        self.lives = 3

    def run(self):
        # Draw Space
        self.space.fill([0, 0, 0])  # Black
        # Draw objects (ship, rocks, etc...)
        self.ship.update()
        self.rock.update()
        # Join everything
        self.screen.blit(self.space, [0, 0])
        return False

    def stop(self):
        pygame.event.clear()
        self.running = False

    def control(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.stop()
            if event.key == K_UP:
                self.ship.thrust_on()
            if event.key == K_RIGHT:
                self.ship.decrement_angle_vel()
            if event.key == K_LEFT:
                self.ship.increment_angle_vel()
            if event.key == K_SPACE:
                self.ship.shoot()
        if event.type == KEYUP:
            if event.key == K_UP:
                self.ship.thrust_off()


class Ship:
    def __init__(self, screen):
        self.screen = screen
        self.set()

    def set(self):
        self.screen_reset()
        self.reset()

    def reset(self):
        self.position = [self.screen_size[0] / 2,
                         self.screen_size[1] / 2]
        self.speed = [0, 0]
        self.angle = math.pi / -2
        self.thrust = False
        self.angle_vel = 0

    def screen_reset(self):
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]

    def start(self):
        ship_size = [31, 31]
        position = [0, 0]
        ship = pygame.Surface(ship_size, SRCALPHA)
        # ship.fill([50, 50, 50])  # FIXME: Remove after tests
        pygame.draw.polygon(ship, (200, 200, 200),
                            [(0, 30), (15, 0), (30, 30), (15, 23)], 1)
        self.ship = pygame.Surface([48, 48], SRCALPHA)
        # self.ship.fill([20, 20, 20])  # FIXME: Remove after tests
        ship = pygame.transform.rotate(ship, 90)
        position[0] = self.ship.get_rect().center[0] - ship.get_rect().center[0]
        position[1] = self.ship.get_rect().center[1] - ship.get_rect().center[1]
        self.ship.blit(ship, position)
        # TODO: Draw thrust when ship is moving
        if self.thrust:
            pass

    def update(self):
        # Angle
        acc = []
        self.angle += self.angle_vel
        # Position
        self.position[0] = ((self.position[0] + self.speed[0]) %
                            self.screen_size[0])
        self.position[1] = ((self.position[1] + self.speed[1]) %
                            self.screen_size[1])
        # Speed
        if self.thrust:
            acc = [-math.cos(self.angle), math.sin(self.angle)]
            self.speed[0] += acc[0] * .2
            self.speed[1] += acc[1] * .2
        # Slow down
        self.speed[0] *= .99
        self.speed[1] *= .99
        # Draw
        orig_rect = self.ship.get_rect()
        rot_image = pygame.transform.rotate(self.ship, math.degrees(self.angle))
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        ship = rot_image.subsurface(rot_rect).copy()
        # ship = pygame.transform.rotate(self.ship, math.degrees(self.angle))
        self.screen.blit(ship, [self.position[0]-24, self.position[1]-24])

    def thrust_on(self):
        # TODO: Play sound using code here
        # ship_thrust_sound.rewind()
        # ship_thrust_sound.play()
        self.thrust = True

    def thrust_off(self):
        # ship_thrust_sound.pause()
        self.thrust = False

    def increment_angle_vel(self):
        self.angle_vel += math.radians(math.pi / 50)

    def decrement_angle_vel(self):
        self.angle_vel -= math.radians(math.pi / 50)

    def shoot(self):
        forward = angle_to_vector(self.angle)
        missile_pos = [self.position[0] + self.radius * forward[0],
                       self.position[1] + self.radius * forward[1]]
        missile_vel = [self.speed[0] + 6 * forward[0],
                       self.speed[1] + 6 * forward[1]]
        a_missile = Sprite(missile_pos, missile_vel, self.angle, 0,
                           missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)

    def get_position(self):
        return self.position

    def get_radius(self):
        return self.radius


class Sprite:
    def __init__(self, screen):
        self.screen = screen
        self.set()

    def set(self):
        self.screen_reset()
        self.reset()

    def reset(self):
        self.position = [self.screen_size[0] / 2,
                         self.screen_size[1] / 2]
        self.speed = [0, 0]
        self.angle = math.pi / -2
        self.angle_vel = 0

    def screen_reset(self):
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]

    def start(self):
        ship_size = [31, 31]
        position = [0, 0]
        ship = pygame.Surface(ship_size, SRCALPHA)
        # ship.fill([50, 50, 50])  # FIXME: Remove after tests
        color_tone = random.randrange(50, 200)
        pygame.draw.polygon(ship, 
                            [color_tone, color_tone, color_tone],
                            [(random.randrange(0, 10), random.randrange(0, 15)),
                             (random.randrange(10, 20), random.randrange(0, 15)),
                             (random.randrange(25, 30), random.randrange(0, 15)),
                             (random.randrange(25, 30), random.randrange(20, 30)),
                             (random.randrange(10, 20), random.randrange(20, 30)),
                             (random.randrange(0, 10), random.randrange(20, 30)),
                             ], 0)
        self.ship = pygame.Surface([48, 48], SRCALPHA)
        # self.ship.fill([20, 20, 20])  # FIXME: Remove after tests
        ship = pygame.transform.rotate(ship, 90)
        position[0] = self.ship.get_rect().center[0] - ship.get_rect().center[0]
        position[1] = self.ship.get_rect().center[1] - ship.get_rect().center[1]
        self.ship.blit(ship, position)

    def update(self):
        # Angle
        acc = []
        self.angle += self.angle_vel
        # Position
        self.position[0] = ((self.position[0] + self.speed[0]) %
                            self.screen_size[0])
        self.position[1] = ((self.position[1] + self.speed[1]) %
                            self.screen_size[1])
        # Draw
        ship = pygame.transform.rotate(self.ship, math.degrees(self.angle))
        self.screen.blit(ship, [self.position[0]-24, self.position[1]-24])

    def angle_vel(self, factor):
        self.angle_vel -= math.radians(math.pi / 50)

    def get_position(self):
        return self.position

    def get_radius(self):
        return self.radius
