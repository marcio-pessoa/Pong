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
        self.set()
        self.ship.start()

    def size_set(self):
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.space = pygame.Surface(self.screen_size,
                                    HWSURFACE | SRCALPHA, 32)
        self.space.convert_alpha()

    def set(self):
        self.ship = Ship(self.space)
        self.reset()

    def size_reset(self):
        # Discover new size factor
        x_factor = self.screen.get_size()[0] / self.screen_size[0]
        y_factor = self.screen.get_size()[1] / self.screen_size[1]
        self.size_set()
        self.ship.screen_reset()

    def reset(self):
        self.lives = 3
        self.rock_group = set()
        self.burst = set()
        self.ship.reset()

    def run(self):
        # Draw Space
        self.space.fill([0, 0, 0])  # Black
        # Draw objects (ship, rocks, missiles, etc...)
        self.ship.update()
        self.burst_update()
        self.rock_update()
        self.check_collision()
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
        # Missile against ship
        for i in self.burst:
            if i.get_rect().colliderect(self.ship.get_rect()):
                self.burst.remove(i)
                return

    def rock_update(self):
        # Need more?
        while len(self.rock_group) < 8:
            rock = Sprite(self.space)
            if not rock.get_rect().colliderect(self.ship.get_rect()):
                self.rock_group.add(rock)
        # Update position
        for i in self.rock_group:
            i.update()

    def burst_update(self):
        for i in self.burst:
        # Check shoot age
            if i.age() >= 3000:
                self.burst.remove(i)
                return
        # Update position
            i.update()

    def stop(self):
        pygame.event.clear()
        self.running = False

    def shoot(self):
        # Limit burst size
        if len(self.burst) >= 10:
            return
        # Shoot!
        shoot = Missile(self.space,
                        self.ship.get_position(), self.ship.get_radius(),
                        self.ship.get_speed(), self.ship.get_angle())
        self.burst.add(shoot)

    def control(self, keys):
        print keys
        if K_ESCAPE in keys:
            self.stop()
        if K_UP in keys:
            self.ship.thrust_on()
        if K_UP not in keys:
            self.ship.thrust_off()
        if K_RIGHT in keys:
            self.ship.decrement_angle_vel()
        if K_LEFT in keys:
            self.ship.increment_angle_vel()
        if K_SPACE in keys:
            self.shoot()


class Ship:

    def __init__(self, screen):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.reset()

    def reset(self):
        self.position = [self.screen_size[0] / 2,
                         self.screen_size[1] / 2]
        self.speed = [0, 0]
        self.angle = math.pi / -2
        self.thrust = False
        self.angle_vel = 0

    def start(self):
        ship_size = [31, 31]
        position = [0, 0]
        ship = pygame.Surface(ship_size, SRCALPHA)
        # ship.fill([50, 50, 50])  # FIXME: Remove after tests
        pygame.draw.polygon(ship, (200, 200, 200),
                            [(0, 30), (15, 0), (30, 30), (15, 23)], 0)
        self.ship = pygame.Surface([48, 48], SRCALPHA)
        # self.ship.fill([20, 20, 20])  # FIXME: Remove after tests
        ship = pygame.transform.rotate(ship, 90)
        position[0] = self.ship.get_rect().center[0] - ship.get_rect().center[0]
        position[1] = self.ship.get_rect().center[1] - ship.get_rect().center[1]
        self.ship.blit(ship, position)
        self.__rect = ship.get_rect()
        self.radius = self.ship.get_rect().center[1]
        self.update()

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
        rot_image = pygame.transform.rotozoom(self.ship,
                                              math.degrees(self.angle), 1)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        ship = rot_image.subsurface(rot_rect).copy()
        # ship = pygame.transform.rotate(self.ship, math.degrees(self.angle))
        self.screen.blit(ship, [self.position[0] - 24, 
                                self.position[1] - 24])
        self.rect = self.__rect.move(self.position[0] - 24,
                                     self.position[1] - 24)

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

    def get_rect(self):
        return self.rect

    def get_radius(self):
        return self.radius

    def get_position(self):
        return self.position

    def get_speed(self):
        return self.speed

    def get_angle(self):
        return self.angle


class Missile:

    def __init__(self, screen,
                 ship_position, ship_radius, ship_speed, ship_angle,):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.angle = ship_angle
        forward = [-math.cos(self.angle), math.sin(self.angle)]
        self.position = [ship_position[0] + 18 * forward[0],
                         ship_position[1] + 18 * forward[1]]
        self.speed = [ship_speed[0] + 5 * forward[0],
                      ship_speed[1] + 5 * forward[1]]
        self.radius = 3
        size = [self.radius * 2, self.radius * 2]
        position = [self.radius, self.radius]
        # Draw
        self.missile = pygame.Surface(size, SRCALPHA)
        pygame.draw.circle(self.missile, (255, 255, 255),
                           position, self.radius)
        self.__rect = self.missile.get_rect()
        self.time_born = pygame.time.get_ticks()
        self.update()

    def update(self):
        # Position
        self.position[0] = ((self.position[0] + self.speed[0]) %
                            self.screen_size[0])
        self.position[1] = ((self.position[1] + self.speed[1]) %
                            self.screen_size[1])
        self.rect = self.__rect.move(self.position[0] - self.radius,
                                     self.position[1] - self.radius)
        # Draw
        self.screen.blit(self.missile, [self.position[0] - self.radius,
                                        self.position[1] - self.radius])

    def age(self):
        return pygame.time.get_ticks() - self.time_born

    def get_radius(self):
        return self.radius

    def get_rect(self):
        return self.rect


class Sprite:
    def __init__(self, screen):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.position = [random.uniform(0.0, 1.0) * self.screen_size[0],
                         random.uniform(0.0, 1.0) * self.screen_size[1]]
        self.speed = [random.uniform(-0.5, 0.5),
                      random.uniform(-0.5, 0.5)]
        self.angle = 0
        self.angle_vel = math.radians(math.pi / (random.uniform(-1, 1) * 10.1))
        self.size = [31, 31]
        size = self.size
        position = [0, 0]
        ship = pygame.Surface(self.size, SRCALPHA)
        # ship.fill([50, 50, 50])  # FIXME: Remove after tests
        color_tone = random.randrange(50, 100)
        pygame.draw.polygon(ship,
                            [color_tone, color_tone, color_tone],
                            [(random.uniform(0, size[1] / 4),
                              random.uniform(0, size[1] / 3)),
                             (random.uniform(size[0] / 4, size[1] / 1.5),
                              random.uniform(0, size[1] / 2)),
                             (random.uniform(size[0] / 1.5, size[1]),
                              random.uniform(0, size[1] / 2)),
                             (random.uniform(size[0] / 1.1, size[1]),
                              random.uniform(size[0] / 1.5, size[1])),
                             (random.uniform(size[0] / 3, size[1] / 1.5),
                              random.uniform(size[0] / 1.5, size[1])),
                             (random.uniform(0, size[1] / 4),
                             random.uniform(size[0] / 1.5, size[1])),
                             ], 0)
        self.ship = pygame.Surface([48, 48], SRCALPHA)
        # self.ship.fill([20, 20, 20])  # FIXME: Remove after tests
        position[0] = self.ship.get_rect().center[0] - ship.get_rect().center[0]
        position[1] = self.ship.get_rect().center[1] - ship.get_rect().center[1]
        self.ship.blit(ship, position)
        self.__rect = ship.get_rect()
        __spawn_far = pygame.Surface([80, 80], SRCALPHA).get_rect()
        self.update()

    def upgrade(self, size):
        self.size[0] += size[0]
        self.size[1] += size[1]
        size = self.size
        self.ship = pygame.Surface(self.size, SRCALPHA)
        # self.ship.fill([50, 50, 50])  # FIXME: Remove after tests
        color_tone = random.randrange(50, 100)
        pygame.draw.polygon(self.ship,
                            [color_tone, color_tone, color_tone],
                            [(random.uniform(0, size[1] / 4),
                              random.uniform(0, size[1] / 3)),
                             (random.uniform(size[0] / 4, size[1] / 1.5),
                              random.uniform(0, size[1] / 2)),
                             (random.uniform(size[0] / 1.5, size[1]),
                              random.uniform(0, size[1] / 2)),
                             (random.uniform(size[0] / 1.1, size[1]),
                              random.uniform(size[0] / 1.5, size[1])),
                             (random.uniform(size[0] / 3, size[1] / 1.5),
                              random.uniform(size[0] / 1.5, size[1])),
                             (random.uniform(0, size[1] / 4),
                             random.uniform(size[0] / 1.5, size[1])),
                             ], 0)
        self.__rect = self.ship.get_rect()
        self.update()

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
        orig_rect = self.ship.get_rect()
        rot_image = pygame.transform.rotozoom(self.ship,
                                              math.degrees(self.angle), 1)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        ship = rot_image.subsurface(rot_rect).copy()
        # ship.fill([20, 20, 20])  # FIXME: Remove after tests
        self.radius = ship.get_rect().center[0]
        self.screen.blit(ship, [self.position[0] - self.radius,
                                self.position[1] - self.radius])
        self.rect = self.__rect.move(self.position[0], self.position[1])

    def get_size(self):
        return self.size

    def get_rect(self):
        return self.rect
