#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run.py

Copyright (c) 2014-2018 Márcio Pessoa

Author: Marcio Pessoa <marcio.pessoa@gmail.com>
Contributors: none

Change log: Check CHANGELOG.md file.

"""

try:
    # Required modules
    import os
    import sys
    import argparse
    import pygame
    from pygame.locals import *
    # Myself modules
    from pong import Pong
except ImportError as err:
    print("Could not load module. " + str(err))
    sys.exit(True)


class UserArgumentParser():
    """
    https://docs.python.org/2/library/argparse.html
    http://chase-seibert.github.io/blog/
    """
    def __init__(self):
        self.program_name = "pong"
        self.program_version = "0.2"
        self.program_date = "2018-10-24"
        self.program_description = "Pong"
        self.program_copyright = "Copyright (c) 2014-2018 Marcio Pessoa"
        self.program_license = "GPLv2"
        self.program_website = "http://pessoa.eti.br/"
        self.program_contact = "Marcio Pessoa <marcio.pessoa@gmail.com>"
        header = ('xc <command> [<args>]\n\n')
        footer = (self.program_copyright + '\n' +
                  'License: ' + self.program_license + '\n' +
                  'Website: ' + self.program_website + '\n' +
                  'Contact: ' + self.program_contact + '\n')
        examples = ('examples:\n' +
                    '  run\n')
        self.version = (self.program_name + " " + self.program_version + " (" +
                        self.program_date + ")")
        epilog = (examples + '\n' + footer)
        parser = argparse.ArgumentParser(
            prog=self.program_name,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog,
            add_help=True,
            usage=header)
        parser.add_argument('-V', '--version', action='version',
                            version=self.version,
                            help='show version information and exit')
        if len(sys.argv) < 2:
            self.run()
            sys.exit(False)
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            echoln('Unrecognized command')
            parser.print_help()
            sys.exit(True)
        getattr(self, args.command)()

    def run(self):
        self.window_title = self.program_description
        self.running = True
        self.screen_rate = 30  # FPS
        self.screen_resolution = (480, 320)  # (width, height) pixels
        # Window position
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        # Initialise screen
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_resolution)
        # Window caption
        pygame.display.set_caption(self.window_title)
        # Background
        self.background = pygame.Surface(self.screen.get_size())
        self.background.fill([0, 0, 0])  # Black
        # Set keyboard speed
        pygame.key.set_repeat(1, 100)
        # Clockling
        self.clock = pygame.time.Clock()
        self.pong = Pong(self.screen)
        self.pong.start()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                self.pong.control(event)
            self.pong.run()
            self.clock.tick(self.screen_rate)
            pygame.display.flip()
        sys.exit(False)

    def __ctrl_check(self, event):
        pass


def main():
    UserArgumentParser()


if __name__ == '__main__':
    main()
