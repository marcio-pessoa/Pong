# pylint: disable=too-many-lines
"""
---
name: invasion.py
description: Invasion package file
contributors:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
  designers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
  - name: Nicolas Masaishi Oi Pessoa
    email: masaishi.pessoa@gmail.com
  - name: Gustavo Nuzzo Gass
    email: gustavonuzzogass@gmail.com
change-log:
  2019-09-01:
  - version: 0.5
    Added: Joystick support.
  2019-07-13:
  - version: 0.04
    Fixed: Barrier destruction.
  2019-02-03:
  - version: 0.03
    Added: Minor updates.
  2019-01-30:
  - version: 0.02
    Added: Sound FX.
  2018-12-25:
  - version: 0.01
    Added: Starting a new game.
"""

import random
import pygame
from pygame.locals import *
from tools.font import Font
from tools.sound import Sound
from tools.pytimer.pytimer import Timer


class Invasion:  # pylint: disable=too-many-instance-attributes
    """
    description:
    """

    def __init__(self, screen):
        self._version = 0.5
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0], self.screen.get_size()[1]]
        self.space = pygame.Surface(self.screen_size,
                                    HWSURFACE | SRCALPHA, 32)  # pylint: disable=undefined-variable
        self.space.convert_alpha()
        self.running = True
        self.ship_burst = set()
        self.alien_burst = set()
        self.walls = set()
        self.aliens = set()
        self.explosions = set()
        self.ship = Ship(self.space)
        self.shoot_timer = Timer(50)
        self.march_timer = Timer(1)
        self.scoreboard = Font(self.space)
        self.scoreboard.set_size(3)
        self.scoreboard.set_position([10, 5])
        self.livesboard = Font(self.space)
        self.livesboard.set_size(3)
        self.livesboard.set_position([330, 5])
        self.levelboard = Font(self.space)
        self.levelboard.set_size(3)
        self.levelboard.set_position([580, 5])
        self.gameovermessage = Font(self.space)
        self.gameovermessage.set_size(9)
        self.gameovermessage.set_position([180, 60])
        self.gameovermessage.set_color((230, 230, 230))
        self.sound = Sound()
        self.reset()

    def set(self):
        """
        description:
        """
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
        """
        description:
        """
        self.level = 0
        self.lives = 2
        self.score = 0
        self.start_march_period = 600
        self.set()
        self.level_up()

    def run(self):
        """
        description:
        """
        self.space.fill([0, 0, 0])  # Black
        self.score_update()
        self.burst_update()
        self.walls_update()
        self.ship.update()
        self.aliens_update()
        self.explosions_update()
        self.collision_check()
        self.aliens_check()
        self.lives_check()
        self.screen.blit(self.space, [0, 0])
        return False

    def lives_check(self):
        """
        description:
        """
        if self.lives == 0:
            self.game_over()

    def collision_check(self):  # pylint: disable=too-many-branches
        """
        description:
        """
        # Ship Missle against Alien
        for i in self.aliens:
            for j in self.ship_burst:
                if i.get_rect().colliderect(j.get_rect()):
                    position = i.get_position()
                    explosion = Explosion(self.space, position)
                    self.explosions.add(explosion)
                    self.score += i.get_points()
                    self.aliens.remove(i)
                    self.ship_burst.remove(j)
                    self.sound.tone(400)
                    return
        # Ship Missle against Wall
        for i in self.walls:
            for j in self.ship_burst:
                if i.get_rect().colliderect(j.get_rect()):
                    self.score += i.get_points()
                    if i.add_damage() <= 0:
                        self.walls.remove(i)
                    self.ship_burst.remove(j)
                    self.sound.tone(200)
                    return
        # Alien Missle against Wall
        for i in self.walls:
            for j in self.alien_burst:
                if i.get_rect().colliderect(j.get_rect()):
                    if i.add_damage() <= 0:
                        self.walls.remove(i)
                    self.alien_burst.remove(j)
                    self.sound.tone(200)
                    return
        # Alien against Wall
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
                    self.sound.tone(200)
                    return
        # Ship against Alien
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
                self.sound.tone(200)
                return
        # Alien Missle againt Ship
        for i in self.alien_burst:
            if i.get_rect().colliderect(self.ship.get_rect()):
                position = self.ship.get_position()
                explosion = Explosion(self.space, position)
                self.explosions.add(explosion)
                self.alien_burst.remove(i)
                self.lives -= 1
                self.sound.tone(200)
                return

    def burst_update(self):
        """
        description:
        """
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
        """
        description:
        """
        formation = (7, 6)
        for cartesian_y in range(formation[1]):
            for cartesian_x in range(formation[0]):
                monster = Monster(self.space, cartesian_y,
                                  [(self.screen_size[0] /
                                    formation[0]) * cartesian_x +
                                   (self.screen_size[0] /
                                    formation[0]) / 3,
                                   ((self.screen_size[1] /
                                     (formation[1] + 3) * cartesian_y)) + 30])
                self.aliens.add(monster)

    def aliens_update(self):
        """
        description:
        """
        # Update
        for i in self.aliens:
            i.update()
        if self.lives == 0:
            return
        if self.march_timer.check():
            self.sound.tone(600)
            # Aliens lateral boundaries
            for i in self.aliens:
                if not self.space.get_rect().contains(i.get_rect()):
                    self.way = not self.way
                    if self.way:
                        self.drop = True
                        self.march_period /= 1.15
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
        """
        description:
        """
        self.ship.stop()
        for i in self.aliens:
            i.stop()
        for i in self.ship_burst:
            i.stop()
        for i in self.alien_burst:
            i.stop()
        self.gameovermessage.echo("GAME OVER")

    def aliens_check(self):
        """
        description:
        """
        if len(self.aliens) == 0:
            self.level_up()

    def level_up(self):
        """
        description:
        """
        self.level += 1
        self.lives += 1
        self.alien_burst_seed -= self.level * 100
        self.start_march_period -= self.start_march_period * self.level / 20
        self.set()

    def walls_deploy(self):
        """
        description:
        """
        quantity = 4
        for i in range(quantity):
            position = (self.screen.get_size()[0] / quantity * i +
                        (self.screen.get_size()[0] / quantity / 2 - 24), 400)
            barrier = Barrier(self.space, position)
            self.walls.add(barrier)

    def walls_update(self):
        """
        description:
        """
        for i in self.walls:
            i.update()

    def score_update(self):
        """
        description:
        """
        self.scoreboard.echo(str(self.score))
        self.livesboard.echo(str(self.lives))
        self.levelboard.echo(str(self.level))

    def explosions_update(self):
        """
        description:
        """
        for i in self.explosions:
            i.update()
            if i.is_done():
                self.explosions.remove(i)
                return

    def stop(self):
        """
        description:
        """
        pygame.event.clear()
        self.running = False

    def ship_shoot(self):
        """
        description:
        """
        # Limit shoot frequency
        if not self.shoot_timer.check():
            return
        # Limit burst size
        if len(self.ship_burst) >= 1:
            return
        # Shoot!
        shoot = Missile(self.space,
                        self.ship.get_position(), self.ship.get_radius(), 5)
        self.ship_burst.add(shoot)
        self.sound.tone(1200)

    def control(self, keys, joystick):
        """
        description:
        """
        if joystick:
            if joystick['hat'][0]['x'] < 0 or \
               joystick['axis'][0] < 0:
                self.ship.move_left()
            if joystick['hat'][0]['x'] > 0 or \
               joystick['axis'][0] > 0:
                self.ship.move_right()
            if joystick['button'][10]:
                self.reset()
            if joystick['button'][0] or joystick['button'][7]:
                self.ship_shoot()
        if K_ESCAPE in keys:  # pylint: disable=undefined-variable
            self.stop()
        if K_RIGHT in keys:  # pylint: disable=undefined-variable
            self.ship.move_right()
        if K_LEFT in keys:  # pylint: disable=undefined-variable
            self.ship.move_left()
        if K_SPACE in keys or K_a in keys:  # pylint: disable=undefined-variable
            self.ship_shoot()
        if K_RETURN in keys:  # pylint: disable=undefined-variable
            self.reset()


class Ship:  # pylint: disable=too-many-instance-attributes
    """
    description:
    """

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
        self.shape = pygame.Surface(self.size, SRCALPHA)  # pylint: disable=undefined-variable
        draw(self.shape, sprite, self.color, 4)
        self.radius = self.shape.get_rect().center[0]
        self.update()

    def reset(self):
        """
        description:
        """
        self.position = [self.screen_size[0] / 2,
                         self.screen_size[1] - self.size[1]]
        self.start()

    def update(self):
        """
        description:
        """
        if self.position[0] < 0:
            self.position[0] = 0
        if self.position[0] + self.size[0] > self.screen.get_size()[0]:
            self.position[0] = self.screen.get_size()[0] - self.size[0]
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def move_right(self):
        """
        description:
        """
        if not self.enable:
            return
        self.position[0] += self.move_increment

    def move_left(self):
        """
        description:
        """
        if not self.enable:
            return
        self.position[0] -= self.move_increment

    def get_rect(self):
        """
        description:
        """
        return self.rect

    def get_radius(self):
        """
        description:
        """
        return self.radius

    def get_position(self):
        """
        description:
        """
        return self.position

    def start(self):
        """
        description:
        """
        self.enable = True

    def stop(self):
        """
        description:
        """
        self.enable = False


class Missile:   # pylint: disable=too-many-arguments,too-many-instance-attributes
    """
    description:
    """

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
        # position = ship_position
        self.shape = pygame.Surface(self.size, SRCALPHA)  # pylint: disable=undefined-variable
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
        """
        description:
        """
        if self.enable:
            self.position[1] = self.position[1] - self.speed
        if self.position[1] < 0:
            self.out = True
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def is_out(self):
        """
        description:
        """
        return self.out

    def get_rect(self):
        """
        description:
        """
        return self.rect

    def stop(self):
        """
        description:
        """
        self.enable = False

    def start(self):
        """
        description:
        """
        self.enable = True


class Monster:  # pylint: disable=too-many-instance-attributes
    """
    description:
    """

    def __init__(self, screen, aspect, position):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.aspect = aspect % 6
        self.__color = []
        self.position = position
        self.alien = self.sprite(self.aspect)
        self.size = [48, 32]
        self.color = self.color(self.aspect)
        self.shape = pygame.Surface(self.size, SRCALPHA)
        self.caray = 0
        self.radius = self.shape.get_rect().center[0]
        draw(self.shape, self.alien[0], self.color, 4)
        self.points = 10 - aspect
        self.enable = True
        self.update()

    def color(self, monster):
        """
        description:
        """
        self.__color = \
            [
                (150, 200, 100),
                (200, 200, 100),
                (100, 200, 200),
                (200, 100, 200),
                (100, 100, 200),
                (200, 100, 100)
            ]
        return self.__color[monster]

    def sprite(self, monster):
        """
        description:
        """
        aliens = []
        aliens.append((
            (
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
        aliens.append((
            (
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
                " #        # ",)
            ))
        aliens.append((
            (
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
        aliens.append((
            (
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
        aliens.append((
            (
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
        aliens.append((
            (
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
        aliens.append((
            (
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
        aliens.append((
            (
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
        aliens.append((
            (
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
        """
        description:
        """
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def march(self, way, drop):
        """
        description:
        """
        if not self.enable:
            return
        if way:
            increment = 1
        else:
            increment = -1
        self.position[0] += increment * 4
        if drop:
            self.position[1] += increment * 16
        draw(self.shape, self.alien[self.caray], self.color, 4)
        self.caray = (self.caray + 1) % 2

    def get_position(self):
        """
        description:
        """
        return self.position

    def get_radius(self):
        """
        description:
        """
        return self.radius

    def get_size(self):
        """
        description:
        """
        return self.size

    def get_points(self):
        """
        description:
        """
        return self.points

    def get_rect(self):
        """
        description:
        """
        return self.rect

    def stop(self):
        """
        description:
        """
        self.enable = False

    def start(self):
        """
        description:
        """
        self.enable = True


class Barrier:  # pylint: disable=too-many-instance-attributes
    """
    description:
    """

    def __init__(self, screen, position):
        self.screen = screen
        self.screen_size = [self.screen.get_size()[0],
                            self.screen.get_size()[1]]
        self.position = position
        self.size = [48, 32]
        self.color = (139, 105, 20)
        self.sprites = (
            (
                "            ",
                "            ",
                "            ",
                "            ",
                "            ",
                "     ####   ",
                "  ######### ",
                "###      ###",
                ),
            (
                "            ",
                "            ",
                "            ",
                "            ",
                "      ##    ",
                "    #####   ",
                " ########## ",
                "###      ###",
                ),
            (
                "            ",
                "            ",
                "     ##     ",
                "   ######   ",
                "    ######  ",
                "  ########  ",
                "############",
                "###      ###",
                ),
            (
                "            ",
                "            ",
                "     ##     ",
                "   ######   ",
                "   #######  ",
                " ########## ",
                "############",
                "###      ###",
                ),
            (
                "            ",
                "    ###     ",
                "   #####    ",
                "  ########  ",
                "  ########  ",
                "########### ",
                "############",
                "###      ###",
                ),
            (
                "    ####    ",
                "  ########  ",
                " ########## ",
                " ########## ",
                " ########## ",
                "############",
                "############",
                "###      ###",
                )
            )
        self.status = len(self.sprites) - 1
        self.shape = pygame.Surface(self.size, SRCALPHA)  # pylint: disable=undefined-variable
        draw(self.shape, self.sprites[self.status], self.color, 4)
        self.update()
        self.points = 1

    def update(self):
        """
        description:
        """
        self.rect = self.shape.get_rect().move(self.position)
        self.screen.blit(self.shape, self.position)

    def add_damage(self):
        """
        description:
        """
        self.status -= 1
        draw(self.shape, self.sprites[self.status], self.color, 4)
        return self.status

    def get_points(self):
        """
        description:
        """
        return self.points

    def get_position(self):
        """
        description:
        """
        return self.position

    def get_rect(self):
        """
        description:
        """
        return self.rect


class Explosion:  # pylint: disable=too-many-instance-attributes
    """
    description:
    """

    def __init__(self, screen, position):
        self.screen = screen
        self.position = position
        self.update_timer = Timer(50)
        self.done = False
        self.sprites = (
            (
                "     ##     ",
                "   ######   ",
                " ########## ",
                "############",
                "############",
                " ########## ",
                "   ######   ",
                "     ##     ",
                ),
            (
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
                ),
            (
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
        self.shape = pygame.Surface(self.size, SRCALPHA)  # pylint: disable=undefined-variable
        self.sprite = self.sprites[self.frame]
        self.update()

    def update(self):
        """
        description:
        """
        if self.update_timer.check():
            self.frame += 1
            if self.frame >= len(self.sprites):
                self.done = True
                return
            self.sprite = self.sprites[self.frame]
        draw(self.shape, self.sprite, self.color, 4)
        self.screen.blit(self.shape, self.position)

    def is_done(self):
        """
        description:
        """
        return self.done


def draw(shape, sprite, color, zoom, offset=None):
    """
    description:
    """
    if offset is None:
        offset = [0, 0]
    x_axis = offset[0]
    y_axis = offset[1]
    shape.fill((0, 0, 0))
    for row in sprite:
        for col in row:
            if col == "#":
                pygame.draw.rect(shape, color, (x_axis, y_axis, zoom, zoom))
            x_axis += zoom
        y_axis += zoom
        x_axis = offset[0]
