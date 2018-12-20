"""
---
name: invasion.py
description: Invasion package file
contributors:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
  designers:
  - name: Nicolas Masaishi Oi Pessoa
    email: masaishi.pessoa@gmail.com
  - name: Gustavo Nuzzo Gass
    email: gustavonuzzogass@gmail.com
  beta-testers:
  - name: Gustavo Nuzzo Gass
    email: gustavonuzzogass@gmail.com
  - name: Nicolas Masaishi Oi Pessoa
    email: masaishi.pessoa@gmail.com
change-log:
  2018-12-25:
  - version: 0.01
    Added: Starting a new game.
"""

import pygame
from pygame.locals import *
import random
from tools.timer import Timer


class Invasion:

    def __init__(self, screen):
        self.version = '0.01'
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.space = pygame.Surface(self.screen_size,
                                    HWSURFACE | SRCALPHA, 32)
        self.space.convert_alpha()
        self.running = True
        self.ship = Ship(self.space)
        self.shoot_timer = Timer(50)
        self.march_timer = Timer(1)
        self.reset()

    def set(self):
        self.ship_burst = set()
        self.alien_burst = set()
        self.walls = set()
        self.aliens = set()
        self.explosions = set()
        self.alien_burst_seed = 2000
        self.march_period = self.start_march_period
        self.march_timer.set(self.march_period)
        self.way = True
        self.drop = False
        self.ship.reset()
        self.walls_deploy()
        self.aliens_deploy()

    def reset(self):
        self.level = 0
        self.lives = 2
        self.score = 0
        self.start_march_period = 600
        self.set()
        self.level_up()

    def run(self):
        # Draw Space
        self.space.fill([0, 0, 0])  # Black
        # Draw objects (ship, rocks, missiles, etc...)
        self.score_update()
        self.burst_update()
        self.walls_update()
        self.ship.update()
        self.aliens_update()
        self.explosions_update()
        self.collision_check()
        self.aliens_check()
        self.lives_check()
        # Join everything
        self.screen.blit(self.space, [0, 0])
        return False

    def lives_check(self):
        if self.lives == 0:
            self.game_over()

    def collision_check(self):
        # Missle againt Alien
        for i in self.aliens:
            for j in self.ship_burst:
                if i.get_rect().colliderect(j.get_rect()):
                    position = i.get_position()
                    explosion = Explosion(self.space, position)
                    self.explosions.add(explosion)
                    self.score += i.get_points()
                    self.aliens.remove(i)
                    self.ship_burst.remove(j)
                    return
        # Alien againt Wall
        for i in self.aliens:
            for j in self.walls:
                if i.get_rect().colliderect(j.get_rect()):
                    position = i.get_position()
                    explosion = Explosion(self.space, position)
                    self.explosions.add(explosion)
                    position = j.get_position()
                    explosion = Explosion(self.space, position)
                    self.explosions.add(explosion)
                    self.aliens.remove(i)
                    self.walls.remove(j)
                    return
        # Ship againt Alien
        for i in self.aliens:
            if i.get_rect().colliderect(self.ship.get_rect()):
                position = i.get_position()
                explosion = Explosion(self.space, position)
                self.explosions.add(explosion)
                position = self.ship.get_position()
                explosion = Explosion(self.space, position)
                self.explosions.add(explosion)
                self.aliens.remove(i)
                self.lives -= 1
                return
        # Ship againt Missle
        for i in self.alien_burst:
            if i.get_rect().colliderect(self.ship.get_rect()):
                position = self.ship.get_position()
                explosion = Explosion(self.space, position)
                self.explosions.add(explosion)
                self.alien_burst.remove(i)
                self.lives -= 1
                return

    def burst_update(self):
        # Update position
        for i in self.ship_burst:
            i.update()
        for i in self.alien_burst:
            i.update()
        # Check shoot age
        for i in self.ship_burst:
            if i.is_out():
                self.ship_burst.remove(i)
                break

    def aliens_deploy(self):
        formation = (8, 6)
        for y in range(formation[1]):
            for x in range(formation[0]):
                monster = Monster(self.space, y,
                                  [(self.screen_size[0] /
                                    formation[0]) * x +
                                   (self.screen_size[0] /
                                    formation[0]) / 3,
                                   ((self.screen_size[1] /
                                    (formation[1] + 3) * y)) + 30],
                                  [200, 200, 200])
                self.aliens.add(monster)

    def aliens_update(self):
        # Update
        for i in self.aliens:
            i.update()
        if self.lives == 0:
            return
        if self.march_timer.check():
            # Aliens lateral boundaries
            for i in self.aliens:
                if not self.space.get_rect().contains(i.get_rect()):
                    self.way = not self.way
                    if self.way:
                        self.drop = True
                        self.march_period /= 1.5
                        self.march_timer.set(self.march_period)
                    break
            # Aliens fall down
            for i in self.aliens:
                i.march(self.way, self.drop)
            self.drop = False
        # Aliens landing
        for i in self.aliens:
            if i.get_position()[1] + i.get_size()[1] >= self.screen_size[1]:
                self.game_over()
                break
        # Fire
        for i in self.aliens:
            i.update()
            if random.randrange(self.alien_burst_seed) == 1:
                shoot = Missile(self.space,
                                i.get_position(), i.get_radius(), 4, -1)
                self.alien_burst.add(shoot)
                break

    def game_over(self):
        self.ship.stop()
        for i in self.aliens:
            i.stop()
        for i in self.ship_burst:
            i.stop()
        for i in self.alien_burst:
            i.stop()
        echo(self.space, "GAME OVER", 12, [20, 60])

    def aliens_check(self):
        if len(self.aliens) == 0:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.lives += 1
        self.alien_burst_seed -= self.level * 100
        self.start_march_period -= self.start_march_period * self.level / 20
        self.set()

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

    def score_update(self):
        echo(self.space, str(self.score), 3, [10, 5])
        echo(self.space, str(self.lives), 3, [380, 5])
        echo(self.space, "LEVEL " + str(self.level), 3, [600, 5])

    def explosions_update(self):
        for i in self.explosions:
            i.update()
            if i.is_done():
                self.explosions.remove(i)
                return

    def stop(self):
        pygame.event.clear()
        self.running = False

    def ship_shoot(self):
        # Timer
        if not self.shoot_timer.check():
            return
        # Limit burst size
        if len(self.ship_burst) >= 1:
            return
        # Shoot!
        shoot = Missile(self.space,
                        self.ship.get_position(), self.ship.get_radius(), 5)
        self.ship_burst.add(shoot)

    def control(self, keys):
        if K_ESCAPE in keys:
            self.stop()
        if K_RIGHT in keys:
            self.ship.move_right()
        if K_LEFT in keys:
            self.ship.move_left()
        if K_SPACE in keys or \
           K_a in keys:
            self.ship_shoot()
        if K_RETURN in keys:
            self.reset()


class Ship:

    def __init__(self, screen):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.size = [48, 32]
        self.color = (180, 180, 240)
        self.enable = True
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
        self.start()

    def update(self):
        if self.position[0] < 0:
            self.position[0] = 0
        if self.position[0] + self.size[0] > self.screen.get_size()[0]:
            self.position[0] = self.screen.get_size()[0] - self.size[0]
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def move_right(self):
        if not self.enable:
            return
        self.position[0] += self.move_increment

    def move_left(self):
        if not self.enable:
            return
        self.position[0] -= self.move_increment

    def get_rect(self):
        return self.rect

    def get_radius(self):
        return self.radius

    def get_position(self):
        return self.position

    def start(self):
        self.enable = True

    def stop(self):
        self.enable = False


class Missile:
    def __init__(self, screen, ship_position, offset, speed, direction=1):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.out = False
        self.size = [8, 16]
        self.speed = speed * direction
        self.color = (250, 250, 250)
        sprite = (
            "##",
            "##",
            "##",
            "##",
            )
        position = ship_position
        self.shape = pygame.Surface(self.size, SRCALPHA)
        draw(self.shape, sprite, self.color, 4)
        if direction == 1:
            self.position = [ship_position[0] + offset - self.size[0] / 2,
                             ship_position[1] - self.size[1]]
        elif direction == -1:
            self.position = [ship_position[0] + offset - self.size[0] / 2,
                             ship_position[1] + self.size[1] + 20]
        self.enable = True
        self.update()

    def update(self):
        if self.enable:
            self.position[1] = self.position[1] - self.speed
        if self.position[1] < 0:
            self.out = True
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def is_out(self):
        return self.out

    def get_rect(self):
        return self.rect

    def stop(self):
        self.enable = False

    def start(self):
        self.enable = True


class Monster:
    def __init__(self, screen, aspect, position, color):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.aspect = aspect % 6
        self.position = position
        self.alien = self.sprite(self.aspect)
        self.size = [48, 32]
        self.color = self.color(aspect % 6)
        self.shape = pygame.Surface(self.size, SRCALPHA)
        self.caray = 0
        self.radius = self.shape.get_rect().center[0]
        draw(self.shape, self.alien[0], self.color, 4)
        self.points = 10 - aspect
        self.enable = True
        self.update()

    def color(self, monster):
        aliens = []
        aliens.append((150, 200, 100))
        aliens.append((200, 200, 100))
        aliens.append((100, 200, 200))
        aliens.append((200, 100, 200))
        aliens.append((100, 100, 200))
        aliens.append((200, 100, 100))
        return aliens[monster]

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
            "#####  #####",
            "# ######## #",
            "#  ######  #",
            "#  ######   ",
            "#   ####    ",
            "    #  #    ",
            "    #  ##   ",
            ), (
            "    ####    ",
            "#####  #####",
            "# ######## #",
            "#  ######  #",
            "   ######  #",
            "    ####   #",
            "    #  #    ",
            "   ##  #    ",
            )))
        aliens.append(((
            "   ##  ##   ",
            "     ##     ",
            "#### ## ####",
            " ########## ",
            "  ########  ",
            "   ######   ",
            "    #  #    ",
            "    #  #    ",
            ), (
            "   ##  ##   ",
            "     ##     ",
            "  ## ## ##  ",
            "  ########  ",
            "   ######   ",
            "    ####    ",
            "    #  #    ",
            "    #  #    ",
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
        aliens.append(((
            "  #      #  ",
            "   #    #   ",
            "   ######   ",
            " # ##  ## # ",
            " ########## ",
            " #   ##   # ",
            " #       # #",
            "# #         ",
            ), (
            "  #      #  ",
            "   #    #   ",
            "   ######   ",
            " # ##  ## # ",
            " ########## ",
            " #   ##   # ",
            "# #       # ",
            "         # #",
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
            "            ",
            "     ###    ",
            "    #   #   ",
            "        #   ",
            "       #    ",
            "      #     ",
            "            ",
            "      #     ",
            ), (
            "            ",
            "     ###    ",
            "    #   #   ",
            "    #       ",
            "     #      ",
            "      #     ",
            "            ",
            "      #     ",
            )))
        return aliens[monster]

    def update(self):
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def march(self, way, drop):
        if not self.enable:
            return
        # Position
        if way:
            increment = 1
        else:
            increment = -1
        self.position[0] += increment * 4
        if drop:
            self.position[1] += increment * 16
        # Look
        draw(self.shape, self.alien[self.caray], self.color, 4)
        self.caray = (self.caray + 1) % 2

    def get_position(self):
        return self.position

    def get_radius(self):
        return self.radius

    def get_size(self):
        return self.size

    def get_points(self):
        return self.points

    def get_rect(self):
        return self.rect

    def stop(self):
        self.enable = False

    def start(self):
        self.enable = True


class Barrier:

    def __init__(self, screen, position):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.position = position
        self.size = [48, 32]
        self.color = (139, 105, 20)
        sprite = (
            "    ####    ",
            "  ########  ",
            " ########## ",
            " ########## ",
            " ########## ",
            "############",
            "############",
            "###      ###",
            )
        self.shape = pygame.Surface(self.size, SRCALPHA)
        draw(self.shape, sprite, self.color, 4)
        self.update()

    def update(self):
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def get_position(self):
        return self.position

    def get_rect(self):
        return self.rect


class Explosion:

    def __init__(self, screen, position):
        self.screen = screen
        self.position = position
        self.update_timer = Timer(50)
        self.done = False
        self.sprites = ((
            "     ##     ",
            "   ######   ",
            " ########## ",
            "############",
            "############",
            " ########## ",
            "   ######   ",
            "     ##     ",
            ), (
            "            ",
            "     ##     ",
            "   ######   ",
            " ########## ",
            " ########## ",
            "   ######   ",
            "     ##     ",
            "            ",
            ), (
            "            ",
            "            ",
            "     ##     ",
            "   ######   ",
            "   ######   ",
            "     ##     ",
            "            ",
            "            ",
            ), (
            "            ",
            "            ",
            "            ",
            "     ##     ",
            "     ##     ",
            "            ",
            "            ",
            "            ",
            ), (
            "            ",
            "            ",
            "    #  #    ",
            "     ##     ",
            "     ##     ",
            "    #  #    ",
            "            ",
            "            ",
            ), (
            "            ",
            "   #    #   ",
            "    #  #    ",
            "     ##     ",
            "     ##     ",
            "    #  #    ",
            "   #    #   ",
            "            ",
            ), (
            "  #      #  ",
            "   #    #   ",
            "    #  #    ",
            "     ##     ",
            "     ##     ",
            "    #  #    ",
            "   #    #   ",
            "  #      #  ",
            ), (
            "  #      #  ",
            "   #    #   ",
            "    #  #  # ",
            "            ",
            " #          ",
            "    #  #    ",
            "   #    #   ",
            "  #      #  ",
            ), (
            "  #      #  ",
            "   #    #   ",
            "            ",
            "            ",
            "            ",
            "            ",
            "   #    #   ",
            "  #      #  ",
            ), (
            "  #      #  ",
            "            ",
            "            ",
            "            ",
            "            ",
            "            ",
            "            ",
            "  #      #  ",
            ))
        self.frame = 0
        self.size = [48, 32]
        self.color = (255, 150, 150)
        self.shape = pygame.Surface(self.size, SRCALPHA)
        self.sprite = self.sprites[self.frame]
        self.update()

    def update(self):
        if self.update_timer.check():
            self.frame += 1
            if self.frame >= len(self.sprites):
                self.done = True
                return
            self.sprite = self.sprites[self.frame]
        draw(self.shape, self.sprite, self.color, 4)
        self.screen.blit(self.shape, self.position)

    def is_done(self):
        return self.done


def draw(shape, sprite, color, zoom, offset=[0, 0]):
    x = offset[0]
    y = offset[1]
    shape.fill((0, 0, 0))
    for row in sprite:
        for col in row:
            if col == "#":
                pygame.draw.rect(shape, color, (x, y, zoom, zoom))
            x += zoom
        y += zoom
        x = offset[0]


def echo(screen, string, size, position):
    alphabet = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                " ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-")
    sprites = ((
        "  ##   ",
        " #  #  ",
        "#    # ",
        "###### ",
        "#    # ",
        "#    # ",
        ), (
        "#####  ",
        "#    # ",
        "#####  ",
        "#    # ",
        "#    # ",
        "#####  ",
        ), (
        " ####  ",
        "#    # ",
        "#      ",
        "#      ",
        "#    # ",
        " ####  ",
        ), (
        "#####  ",
        "#    # ",
        "#    # ",
        "#    # ",
        "#    # ",
        "#####  ",
        ), (
        "###### ",
        "#      ",
        "#####  ",
        "#      ",
        "#      ",
        "###### ",
        ), (
        "###### ",
        "#      ",
        "#####  ",
        "#      ",
        "#      ",
        "#      ",
        ), (
        " ####  ",
        "#    # ",
        "#      ",
        "#  ### ",
        "#    # ",
        " ####  ",
        ), (
        "#    # ",
        "#    # ",
        "###### ",
        "#    # ",
        "#    # ",
        "#    # ",
        ), (
        "###### ",
        "  #    ",
        "  #    ",
        "  #    ",
        "  #    ",
        "###### ",
        ), (
        "     # ",
        "     # ",
        "     # ",
        "     # ",
        "#    # ",
        " ####  ",
        ), (
        "#    # ",
        "#   #  ",
        "####   ",
        "#  #   ",
        "#   #  ",
        "#    # ",
        ), (
        "#      ",
        "#      ",
        "#      ",
        "#      ",
        "#      ",
        "###### ",
        ), (
        "#    # ",
        "##  ## ",
        "# ## # ",
        "#    # ",
        "#    # ",
        "#    # ",
        ), (
        "#    # ",
        "##   # ",
        "# #  # ",
        "#  # # ",
        "#   ## ",
        "#    # ",
        ), (
        " ####  ",
        "#    # ",
        "#    # ",
        "#    # ",
        "#    # ",
        " ####  ",
        ), (
        "#####  ",
        "#    # ",
        "#    # ",
        "#####  ",
        "#      ",
        "#      ",
        ), (
        " ####  ",
        "#    # ",
        "#    # ",
        "#  # # ",
        "#   #  ",
        " ### # ",
        ), (
        "#####  ",
        "#    # ",
        "#    # ",
        "#####  ",
        "#   #  ",
        "#    # ",
        ), (
        " ####  ",
        "#      ",
        " ####  ",
        "     # ",
        "#    # ",
        " ####  ",
        ), (
        "###### ",
        "  #    ",
        "  #    ",
        "  #    ",
        "  #    ",
        "  #    ",
        ), (
        "#    # ",
        "#    # ",
        "#    # ",
        "#    # ",
        "#    # ",
        " ####  ",
        ), (
        "#    # ",
        "#    # ",
        "#   #  ",
        "#  #   ",
        "# #    ",
        "##     ",
        ), (
        "#    # ",
        "#    # ",
        "#    # ",
        "# ## # ",
        "##  ## ",
        "#    # ",
        ), (
        "#    # ",
        " #  #  ",
        "  ##   ",
        "  ##   ",
        " #  #  ",
        "#    # ",
        ), (
        "#   ## ",
        " # #   ",
        "  #    ",
        "  #    ",
        "  #    ",
        "  #    ",
        ), (
        "###### ",
        "    #  ",
        "   #   ",
        "  #    ",
        " #     ",
        "###### ",
        ), (
        "        "
        "        "
        "        "
        "        "
        "        "
        "        "
        ), (
        " ####  ",
        "#   ## ",
        "#  # # ",
        "# #  # ",
        "##   # ",
        " ####  ",
        ), (
        "  ##   ",
        " # #   ",
        "#  #   ",
        "   #   ",
        "   #   ",
        "###### ",
        ), (
        " ####  ",
        "#    # ",
        "   ##  ",
        " ##    ",
        "#      ",
        "###### ",
        ), (
        "#####  ",
        "     # ",
        " ####  ",
        "     # ",
        "     # ",
        "#####  ",
        ), (
        "#    # ",
        "#    # ",
        "###### ",
        "     # ",
        "     # ",
        "     # ",
        ), (
        "#####  ",
        "#      ",
        "#####  ",
        "     # ",
        "     # ",
        "#####  ",
        ), (
        " ####  ",
        "#      ",
        "#####  ",
        "#    # ",
        "#    # ",
        " ####  ",
        ), (
        "###### ",
        "    #  ",
        " ##### ",
        "   #   ",
        "   #   ",
        "   #   ",
        ), (
        " ####  ",
        "#    # ",
        " ####  ",
        "#    # ",
        "#    # ",
        " ####  ",
        ), (
        " ####  ",
        "#    # ",
        " ##### ",
        "     # ",
        "     # ",
        " ####  ",
        ), (
        "       ",
        "       ",
        "###### ",
        "       ",
        "       ",
        "       ",
        ))
    increment = 7 * size
    for i in list(string):
        char = alphabet.index(i)
        sprite = sprites[char]
        shape = pygame.Surface((7 * size, 6 * size), SRCALPHA)
        draw(shape, sprite, (200, 200, 200), size, (0, 0))
        screen.blit(shape, position)
        position[0] += increment
