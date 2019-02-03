"""
---
name: fontbasic.py
description: Font Basic package file
contributors:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log:
  2019-02-03:
  - version: 0.01
    Added: New package :-).
"""

import pygame
from pygame.locals import *


class Font:
    def __init__(self, screen):
        self.version = '0.01'
        self.screen = screen
        self.alphabet = (
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
            " ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-")
        self.sprites = ((
            "  #   ",
            " # #  ",
            "#   # ",
            "#   # ",
            "##### ",
            "#   # ",
            "#   # ",
            ), (
            "####  ",
            "#   # ",
            "#   # ",
            "####  ",
            "#   # ",
            "#   # ",
            "####  ",
            ), (
            " ###  ",
            "#   # ",
            "#     ",
            "#     ",
            "#     ",
            "#   # ",
            " ###  ",
            ), (
            "####  ",
            "#   # ",
            "#   # ",
            "#   # ",
            "#   # ",
            "#   # ",
            "####  ",
            ), (
            "##### ",
            "#     ",
            "#     ",
            "####  ",
            "#     ",
            "#     ",
            "##### ",
            ), (
            "##### ",
            "#     ",
            "#     ",
            "####  ",
            "#     ",
            "#     ",
            "#     ",
            ), (
            " ###  ",
            "#   # ",
            "#     ",
            "#  ## ",
            "#   # ",
            "#   # ",
            " ###  ",
            ), (
            "#   # ",
            "#   # ",
            "#   # ",
            "##### ",
            "#   # ",
            "#   # ",
            "#   # ",
            ), (
            "##### ",
            "  #   ",
            "  #   ",
            "  #   ",
            "  #   ",
            "  #   ",
            "##### ",
            ), (
            "    # ",
            "    # ",
            "    # ",
            "    # ",
            "    # ",
            "#   # ",
            " ###  ",
            ), (
            "#   # ",
            "#  #  ",
            "# #   ",
            "###   ",
            "# #   ",
            "#  #  ",
            "#   # ",
            ), (
            "#     ",
            "#     ",
            "#     ",
            "#     ",
            "#     ",
            "#     ",
            "##### ",
            ), (
            "#   # ",
            "#   # ",
            "## ## ",
            "# # # ",
            "#   # ",
            "#   # ",
            "#   # ",
            ), (
            "#   # ",
            "#   # ",
            "##  # ",
            "# # # ",
            "#  ## ",
            "#   # ",
            "#   # ",
            ), (
            " ###  ",
            "#   # ",
            "#   # ",
            "#   # ",
            "#   # ",
            "#   # ",
            " ###  ",
            ), (
            "####  ",
            "#   # ",
            "#   # ",
            "####  ",
            "#     ",
            "#     ",
            "#     ",
            ), (
            " ###  ",
            "#   # ",
            "#   # ",
            "#   # ",
            "# # # ",
            "#  #  ",
            " ## # ",
            ), (
            "####  ",
            "#   # ",
            "#   # ",
            "####  ",
            "# #   ",
            "#  #  ",
            "#   # ",
            ), (
            " ###  ",
            "#   # ",
            "#     ",
            " ###  ",
            "    # ",
            "#   # ",
            " ###  ",
            ), (
            "##### ",
            "  #   ",
            "  #   ",
            "  #   ",
            "  #   ",
            "  #   ",
            "  #   ",
            ), (
            "#   # ",
            "#   # ",
            "#   # ",
            "#   # ",
            "#   # ",
            "#   # ",
            " ###  ",
            ), (
            "#   # ",
            "#   # ",
            "#   # ",
            "#   # ",
            "#   # ",
            " # #  ",
            "  #   ",
            ), (
            "#   # ",
            "#   # ",
            "#   # ",
            "# # # ",
            "## ## ",
            "#   # ",
            "#   # ",
            ), (
            "#   # ",
            "#   # ",
            " # #  ",
            "  #   ",
            " # #  ",
            "#   # ",
            "#   # ",
            ), (
            "#   # ",
            "#   # ",
            "#   # ",
            " # #  ",
            "  #   ",
            "  #   ",
            "  #   ",
            ), (
            "##### ",
            "    # ",
            "   #  ",
            "  #   ",
            " #    ",
            "#     ",
            "##### ",
            ), (
            "       "
            "       "
            "       "
            "       "
            "       "
            "       "
            "       "
            ), (
            " ###  ",
            "#   # ",
            "#  ## ",
            "# # # ",
            "##  # ",
            "#   # ",
            " ###  ",
            ), (
            "  #   ",
            " ##   ",
            "# #   ",
            "  #   ",
            "  #   ",
            "  #   ",
            "##### ",
            ), (
            " ###  ",
            "#   # ",
            "   #  ",
            "  #   ",
            " #    ",
            "#     ",
            "##### ",
            ), (
            "####  ",
            "    # ",
            "    # ",
            " ###  ",
            "    # ",
            "    # ",
            "####  ",
            ), (
            "#     ",
            "#   # ",
            "#   # ",
            "##### ",
            "    # ",
            "    # ",
            "    # ",
            ), (
            "####  ",
            "#     ",
            "#     ",
            "####  ",
            "    # ",
            "    # ",
            "####  ",
            ), (
            " ###  ",
            "#     ",
            "#     ",
            "####  ",
            "#   # ",
            "#   # ",
            " ###  ",
            ), (
            "##### ",
            "    # ",
            "   #  ",
            "  #   ",
            "  #   ",
            "  #   ",
            "  #   ",
            ), (
            " ###  ",
            "#   # ",
            "#   # ",
            " ###  ",
            "#   # ",
            "#   # ",
            " ###  ",
            ), (
            " ###  ",
            "#   # ",
            "#   # ",
            " #### ",
            "    # ",
            "    # ",
            " ###  ",
            ), (
            "      ",
            "  #   ",
            "  #   ",
            "##### ",
            "  #   ",
            "  #   ",
            "      ",
            ), (
            "      ",
            "      ",
            "      ",
            "##### ",
            "      ",
            "      ",
            "      ",
            ))
        self.set_size(1)
        self.position = [0, 0]
        self.color = [200, 200, 200]

    def echo(self, string):
        position = list(self.position)
        for i in list(string):
            char = self.alphabet.index(i)
            sprite = self.sprites[char]
            self.shape = pygame.Surface((6 * self.size, 7 * self.size), SRCALPHA)
            self.shape.fill((0, 0, 0))
            self.draw(sprite, (0, 0))
            self.screen.blit(self.shape, position)
            position[0] += self.increment

    def set_size(self, size):
        self.size = size
        self.increment = 6 * self.size

    def set_position(self, position):
        self.position = position

    def set_color(self, color):
        self.color = color

    def draw(self, sprite, position):
        x = position[0]
        y = position[1]
        for row in sprite:
            for col in row:
                if col == "#":
                    pygame.draw.rect(self.shape, self.color,
                                     (x, y, self.size, self.size))
                x += self.size
            y += self.size
            x = position[0]
