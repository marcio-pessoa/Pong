"""
pong.py

Description: Pong package file

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Change log:
2018-10-26
        * Version: 0.03
        * Added: Window resizing support.

2018-06-20
        * Version: 0.02
        * Fixed: Ball spawn to never raize balls without angle.

2014-06-06
        * Version: 0.01
        * Added: First version.
"""

import pygame
from pygame.locals import *
import random


class Pong:
    def __init__(self, screen):
        self.version = '0.03'
        self.screen = screen
        self.running = False

    def start(self):
        self.running = True
        self.size_set()
        self.pad_acceleration = 1
        self.court_side = 1
        self.reset()
        self.set()
        self.ball_spawn()

    def size_set(self):
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.court = pygame.Surface(self.screen_size)
        self.play_area = pygame.Surface([self.court.get_size()[0] - 2,
                                         self.court.get_size()[1] - 2],
                                        pygame.SRCALPHA, 32)
        self.play_area.convert_alpha()
        # TODO: Set ball size based on both dimensions of window size
        self.ball_radius = int(self.play_area.get_size()[0] * 0.03 / 2)
        self.pad_height_half = int(self.play_area.get_size()[1] * 0.2 / 2)
        self.pad_width = int(self.play_area.get_size()[0] * 0.015)
        self.pad_height = self.pad_height_half * 2

    def size_reset(self):
        # Discover new size factor
        x_factor = self.screen.get_size()[0] / self.screen_size[0]
        y_factor = self.screen.get_size()[1] / self.screen_size[1]
        # Set objects new size
        self.ball_position[0] *= x_factor
        self.ball_position[1] *= y_factor
        # FIXME: Fix pads position
        self.pad1_position *= y_factor 
        self.pad2_position *= y_factor 
        # FIXME: Fix ball speed
        self.ball_velocity[0] *= x_factor
        self.ball_velocity[1] *= y_factor
        self.size_set()

    def set(self):
        self.pad1_position = int(self.play_area.get_size()[1] / 2)
        self.pad2_position = int(self.play_area.get_size()[1] / 2)
        self.pad1_vel = 0
        self.pad2_vel = 0
        self.ball_velocity = [0, 0]
        self.pad1_pressed = False
        self.pad2_pressed = False
        self.ball_position = [self.play_area.get_size()[0] / 2,
                              self.play_area.get_size()[1] / 2]

    def reset(self):
        self.score = [0, 0]

    def draw_ball(self):
        pygame.draw.rect(self.play_area, (200, 200, 200),
                         [self.ball_position[0] - self.ball_radius,
                          self.ball_position[1] - self.ball_radius,
                          self.ball_radius * 2, self.ball_radius * 2])

    def draw_pad1(self):
        self.pad1_position += self.pad1_vel
        if self.pad1_position - self.pad_height_half < 0:
            self.pad1_position = 0 + self.pad_height_half
        if self.pad1_position + self.pad_height_half > self.court.get_size()[1]:
            self.pad1_position = self.court.get_size()[1] - self.pad_height_half
        pygame.draw.rect(self.play_area, (160, 160, 160),
                         [0,
                          self.pad1_position - self.pad_height_half,
                          self.pad_width,
                          self.pad_height])

    def draw_pad2(self):
        self.pad2_position += self.pad2_vel
        if self.pad2_position - self.pad_height_half < 0:
            self.pad2_position = 0 + self.pad_height_half
        if self.pad2_position + self.pad_height_half > self.court.get_size()[1]:
            self.pad2_position = self.court.get_size()[1] - self.pad_height_half
        pygame.draw.rect(self.play_area, (160, 160, 160),
                         [self.play_area.get_size()[0] - self.pad_width,
                          self.pad2_position - self.pad_height_half,
                          self.pad_width,
                          self.pad_height])

    def run(self):
        self.draw_court()
        self.draw_pad1()
        self.draw_pad2()
        self.draw_ball()
        self.ball_check()
        self.screen.blit(self.court, [0, 0])
        self.screen.blit(self.play_area, [1, 1])
        # codeln("    Position: " + str(self.ball_position))
        # codeln("    Velocity: " + str(self.ball_velocity))
        return False

    def stop(self):
        pygame.event.clear()
        self.running = False

    def control(self, event):
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.stop()
            if event.key == K_w:
                self.pad1_vel -= self.pad_acceleration
                self.pad1_pressed += 1
            if event.key == K_s:
                self.pad1_vel += self.pad_acceleration
                self.pad1_pressed += 1
            if event.key == K_UP:
                self.pad2_vel -= self.pad_acceleration
                self.pad2_pressed += 1
            if event.key == K_DOWN:
                self.pad2_vel += self.pad_acceleration
                self.pad2_pressed += 1
        if event.type == KEYUP:
            if event.key == K_w:
                self.pad1_vel = 0
                self.pad1_pressed -= 1
            if event.key == K_s:
                self.pad1_vel = 0
                self.pad1_pressed -= 1
            if event.key == K_UP:
                self.pad2_vel = 0
                self.pad2_pressed -= 1
            if event.key == K_DOWN:
                self.pad2_vel = 0
                self.pad2_pressed -= 1

    def ball_spawn(self):
        """
        initialize ball_pos and ball_vel for new bal in middle of table
        if direction is RIGHT, the ball's velocity is upper right, else
        upper left
        """
        self.set()
        self.ball_velocity[0] = (random.randrange(100, 200) / 60.0 *
                                 self.court_side)
        self.ball_velocity[1] = 0
        # Make sure ball will never run without an angle
        while self.ball_velocity[1] == 0:
            self.ball_velocity[1] = (random.randrange(-100, 100) / 60.0) * -1
        if self.ball_velocity[1] >= -0.5 or self.ball_velocity[1] <= 0.5:
            self.ball_velocity[1] *= 2

    def draw_court(self):
        # Clear court
        self.court.fill([0, 0, 0])  # Black
        self.play_area.fill([0, 0, 0])  # Black
        # Draw gutters
        pygame.draw.line(self.court, (100, 100, 100),
                         [0, 0],
                         [0,
                          self.court.get_size()[1] - 1])
        pygame.draw.line(self.court, (100, 100, 100),
                         [0, 0],
                         [self.court.get_size()[0] - 1, 0])
        pygame.draw.line(self.court, (100, 100, 100),
                         [self.court.get_size()[0] - 1, 0],
                         [self.court.get_size()[0] - 1,
                          self.court.get_size()[1]])
        pygame.draw.line(self.court, (100, 100, 100),
                         [0,
                          self.court.get_size()[1] - 1],
                         [self.court.get_size()[0] - 1,
                          self.court.get_size()[1] - 1])
        # Draw mid dashed line
        for y in range(0, self.play_area.get_size()[1], 5):
            pygame.draw.line(self.play_area, (128, 128, 128),
                             [self.play_area.get_size()[0] / 2,
                              4 + (y * 5)],
                             [self.play_area.get_size()[0] / 2,
                              16 + (y * 5)])

    def ball_check(self):
        # update ball position
        self.ball_position[0] += self.ball_velocity[0]
        self.ball_position[1] += self.ball_velocity[1]
        # Bounces off of the top
        if self.ball_position[1] - self.ball_radius < 0:
            self.ball_velocity[1] *= -1
        # Bounces off of the bottom
        if self.ball_position[1] + self.ball_radius > \
           self.play_area.get_size()[1]:
            self.ball_velocity[1] *= -1
        # Bounces off of the left
        if self.ball_position[0] - self.ball_radius < self.pad_width:
            if ((self.ball_position[1] + self.ball_radius) >
                (self.pad1_position - self.pad_height_half)) and \
               ((self.ball_position[1] - self.ball_radius) <
               (self.pad1_position + self.pad_height_half)):
                self.ball_velocity[0] *= -1.1
                self.ball_velocity[1] *= 1.1
            else:
                self.court_side = -1
                self.ball_spawn()
                self.score[1] += 1
        # Bounces off of the right
        if self.ball_position[0] + self.ball_radius > \
           self.play_area.get_size()[0] - self.pad_width:
            if ((self.ball_position[1] + self.ball_radius) >
                (self.pad2_position - self.pad_height_half)) and \
               ((self.ball_position[1] - self.ball_radius) <
               (self.pad2_position + self.pad_height_half)):
                self.ball_velocity[0] *= -1.1
                self.ball_velocity[1] *= 1.1
            else:
                self.court_side = 1
                self.ball_spawn()
                self.score[0] += 1
