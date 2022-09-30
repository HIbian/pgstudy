import pygame
from settings import *
from support import *


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        # general setup
        self.image = self.animations[self.status][self.frame_index]
        # rect only receive integer,so we use pos fluted instead of rect.
        self.rect = self.image.get_rect(center=pos)

        # movement
        self.direction = pygame.math.Vector2(0, 0)
        # maintain position individually because of rect only require integer.
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': []}
        for animation in self.animations.keys():
            full_path = 'graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)
        print(self.animations)

    def animate(self, dt):
        self.frame_index += 4 * dt
        # self.frame_index = self.frame_index % len(self.animations[self.status])
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        else:
            self.direction.x = 0

    def move(self, dt):
        # normalizing a vector
        if self.direction != (0, 0):
            self.direction = self.direction.normalize()

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y

    def get_status(self):
        if self.direction == (0, 0):
            self.status = self.status.split('_')[0] + '_idle'

    # level.run():self.all_sprites.update() call this function and others which class is a Sprite and override
    # update() function
    def update(self, dt):
        self.input()
        self.move(dt)
        self.get_status()
        self.animate(dt)
