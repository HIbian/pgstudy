import pygame
from settings import *
from support import *
from timer import Timer


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collison_sprites, tree_sprites, interaction_sprites, soil_layer):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        # general setup
        self.image = self.animations[self.status][self.frame_index]
        # rect only receive integer,so we use pos fluted instead of rect.
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        # movement
        self.direction = pygame.math.Vector2(0, 0)
        # maintain position individually because of rect only require integer.
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 500

        # collision
        self.collison_sprites = collison_sprites
        self.hitbox = self.rect.copy().inflate((-126, -70))

        # timers
        self.timers = {
            'tool use': Timer(400, self.use_tool),
            'tool switch': Timer(200),
            'seed use': Timer(200, self.use_seed),
            'seed switch': Timer(200)
        }

        # tools
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        # seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        # inventory
        self.item_inventory = {
            'wood': 0,
            'apple': 0,
            'corn': 0,
            'tomato': 0,
        }

        # interaction
        self.tree_sprites = tree_sprites
        self.interaction_sprites = interaction_sprites
        self.sleep = False
        self.soil_layer = soil_layer

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_pos)

        if self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
        if self.selected_tool == 'water':
            self.soil_layer.water(self.target_pos)

    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def use_seed(self):
        self.soil_layer.plant_seed(self.target_pos, self.selected_seed)

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'left': [], 'right': [],
                           'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
                           'right_hoe': [], 'left_hoe': [], 'up_hoe': [], 'down_hoe': [],
                           'right_water': [], 'left_water': [], 'up_water': [], 'down_water': [],
                           'right_axe': [], 'left_axe': [], 'up_axe': [], 'down_axe': []}
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

        if not self.timers['tool use'].active:
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

            # tool use
            if keys[pygame.K_SPACE]:
                # timer for the tool use
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
            # change tool
            if not self.timers['tool switch'].active and keys[pygame.K_q]:
                self.timers['tool switch'].activate()
                self.tool_index = (self.tool_index + 1) % len(self.tools)
                self.selected_tool = self.tools[self.tool_index]

            # seed use
            if keys[pygame.K_e]:
                # timer for the tool use
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
            # change seed
            if not self.timers['seed switch'].active and keys[pygame.K_LCTRL]:
                self.timers['seed switch'].activate()
                self.seed_index = (self.seed_index + 1) % len(self.seeds)
                self.selected_seed = self.seeds[self.seed_index]

            if keys[pygame.K_RETURN]:
                # False , don't kill self.interaction_sprites
                collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction_sprites, False)
                if collided_interaction_sprite:
                    # todo figure out why we use ...[0].
                    if collided_interaction_sprite[0].name == 'Trader':
                        pass
                    elif collided_interaction_sprite[0].name == 'Bed':
                        self.status = 'left_idle'
                        self.sleep = True

    def collision(self, direction):
        for sprite in self.collison_sprites.sprites():
            if not hasattr(sprite, 'hitbox'):
                continue
            if not sprite.hitbox.colliderect(self.hitbox):
                continue
            if direction == 'horizontal':
                if self.direction.x > 0:  # moving right
                    self.hitbox.right = sprite.hitbox.left
                if self.direction.x < 0:  # moving left
                    self.hitbox.left = sprite.hitbox.right
                self.rect.centerx = self.hitbox.centerx
                self.pos.x = self.hitbox.centerx
            elif direction == 'vertical':
                if self.direction.y < 0:  # moving right
                    self.hitbox.top = sprite.hitbox.bottom
                if self.direction.y > 0:  # moving left
                    self.hitbox.bottom = sprite.hitbox.top
                self.rect.centery = self.hitbox.centery
                self.pos.y = self.hitbox.centery

    def move(self, dt):
        # normalizing a vector
        if self.direction != (0, 0):
            self.direction = self.direction.normalize()

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def get_status(self):
        if self.direction == (0, 0):
            self.status = self.status.split('_')[0] + '_idle'

        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            if timer.active:
                timer.update()

    # level.run():self.all_sprites.update() call this function and others which class is a Sprite and override
    # update() function
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)
