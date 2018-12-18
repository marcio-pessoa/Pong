#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
---
name: marcade.py
description: Invasion package file
copyright: 2014-2018 Márcio Pessoa
people:
  developers:
  - name: Marcio Pessoa
    email: marcio.pessoa@gmail.com
change-log: Check CHANGELOG.md file.
"""

try:
    import sys
    import argparse
    import os
    import pygame
    from pygame.locals import *
    import random
except ImportError as err:
    print("Could not load module. " + str(err))
    sys.exit(True)


class UserArgumentParser():
    """
    https://docs.python.org/2/library/argparse.html
    http://chase-seibert.github.io/blog/
    """
    def __init__(self):
        self.program_name = "marcade"
        self.program_version = "0.7"
        self.program_date = "2018-11-25"
        self.program_description = "MArcade"
        self.program_copyright = "Copyright (c) 2014-2018 Marcio Pessoa"
        self.program_license = "GPLv2"
        self.program_website = "https://github.com/marcio-pessoa/marcade"
        self.program_contact = "Marcio Pessoa <marcio.pessoa@gmail.com>"
        self.window_title = self.program_description
        self.available_games = ["rocks", "invasion", "pongue"]
        header = ('marcade <game> [<args>]\n\n' +
                  'Games:\n' +
                  '  rocks          based on amazing Asteroids\n' +
                  '  invasion       based on memorable Space Invaders\n' +
                  '  pongue         based on classical Pong\n\n')
        footer = (self.program_copyright + '\n' +
                  'License: ' + self.program_license + '\n' +
                  'Website: ' + self.program_website + '\n' +
                  'Contact: ' + self.program_contact + '\n')
        examples = ('examples:\n' +
                    '  marcade rocks\n' +
                    '  marcade pongue --fullscreen\n')
        self.version = (self.program_name + " " + self.program_version + " (" +
                        self.program_date + ")")
        epilog = (examples + '\n' + footer)
        parser = argparse.ArgumentParser(
            prog=self.program_name,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog,
            add_help=True,
            usage=header)
        parser.add_argument('game', help='game to run')
        parser.add_argument('-V', '--version', action='version',
                            version=self.version,
                            help='show version information and exit')
        if len(sys.argv) < 2:
            # Select a random game
            eval("self." + str(random.choice(self.available_games)) + "()")
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.game):
            print('Unrecognized command')
            parser.print_help()
            sys.exit(True)
        getattr(self, args.game)()

    def __screen_start(self):
        self.running = True
        self.screen_rate = 30  # FPS
        self.canvas_size = (800, 480)  # WVGA (width, height) pixels
        self.__screen_set()
        self.__ctrl_set()

    def __screen_set(self):
        # Window position
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        # Initialise screen
        pygame.init()
        self.__screen_reset()
        # Window caption
        pygame.display.set_caption(self.window_title)
        # Clockling
        self.clock = pygame.time.Clock()

    def __screen_reset(self):
        self.screen = pygame.display.set_mode(self.canvas_size,
                                              HWSURFACE |
                                              DOUBLEBUF |
                                              RESIZABLE)

    def __run(self):
        while self.running:
            self.__check_event()
            self.game.run()
            self.clock.tick(self.screen_rate)
            pygame.display.flip()

    def __check_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                self.keys.add(event.key)
            elif event.type == KEYUP:
                self.keys.remove(event.key)
            elif event.type == VIDEORESIZE:
                self.canvas_size = event.dict['size']
                self.__screen_reset()
                self.game.size_reset()
        self.game.control(self.keys)

    def __ctrl_set(self):
        # Set keyboard speed
        pygame.key.set_repeat(0, 0)
        self.keys = set()

    def pongue(self):
        from games.pongue import Pongue
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' pongue',
            description='based on classical Pong')
        args = parser.parse_args(sys.argv[2:])
        self.window_title = 'Pongue'
        self.__screen_start()
        self.game = Pongue(self.screen)
        self.game.start()
        self.__run()
        sys.exit(False)

    def rocks(self):
        from games.rocks import Rocks
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' rocks',
            description='based on amazing Asteroids')
        args = parser.parse_args(sys.argv[2:])
        self.window_title = 'Asteroids'
        self.__screen_start()
        self.game = Rocks(self.screen)
        self.game.start()
        self.__run()
        sys.exit(False)

    def invasion(self):
        from games.invasion import Invasion
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' invasion',
            description='based on Space Invaders')
        args = parser.parse_args(sys.argv[2:])
        self.window_title = 'Invasion'
        self.__screen_start()
        self.game = Invasion(self.screen)
        self.__run()
        sys.exit(False)


def main():
    UserArgumentParser()


if __name__ == '__main__':
    main()
