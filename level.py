import pygame
from settings import *
from player import Player
from overlay import Overlay

class Level:
    def __init__(self):
        # get_surface() comes from main.Game.__init__():pygame.display.setmode
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        self.player = Player((640, 360), self.all_sprites)

    def run(self, dt):
        self.display_surface.fill('black')
        # self.all_sprites.draw(self.display_surface)
        self.all_sprites.customize_draw()
        self.all_sprites.update(dt)

        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def customize_draw(self):
        for sprite in  self.sprites():
            self.display_surface.blit(sprite.image,sprite.rect)