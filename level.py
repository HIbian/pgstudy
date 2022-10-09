import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction
from pytmx.util_pygame import load_pygame
from support import import_folder


class Level:
    def __init__(self):
        # get_surface() comes from main.Game.__init__():pygame.display.setmode
        self.display_surface = pygame.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        tmx_data = load_pygame('./data/map.tmx')
        # house
        for layers in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layers).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
        for layers in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layers).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites)
        # Fence
        for layers in ['Fence']:
            for x, y, surf in tmx_data.get_layer_by_name(layers).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

        # water
        water_frames = import_folder('./graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            # make sure 'self.all_sprites' is the first Sprite in the array.It's related to
            # sprites.Tree.damage#remove an apple
            Tree(
                pos=(obj.x, obj.y),
                surf=obj.image,
                groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
                name=obj.name,
                player_add=self.player_add
            )

        # wildflowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        # collision tiles
        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic(pos=(x * TILE_SIZE, y * TILE_SIZE), surf=pygame.Surface((TILE_SIZE, TILE_SIZE)),
                    groups=self.collision_sprites)

        Generic(
            pos=(0, 0),
            surf=pygame.image.load('./graphics/world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground']
        )
        # Player setup
        for obj in tmx_data.get_layer_by_name('Player'):
            # set position when level start
            if obj.name == 'Start':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    group=self.all_sprites,
                    collison_sprites=self.collision_sprites,
                    tree_sprites=self.tree_sprites,
                    interaction_sprites=self.interaction_sprites
                )
            # init bed interaction area
            if obj.name == 'Bed':
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

    def player_add(self, item):
        self.player.item_inventory[item] += 1

    def run(self, dt):
        self.display_surface.fill('black')
        # self.all_sprites.draw(self.display_surface)
        self.all_sprites.customize_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def customize_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)

                    # debug
                    if sprite == player:
                        pygame.draw.rect(self.display_surface, 'red', offset_rect, 5)
                        hitbox_rect = player.hitbox.copy()
                        hitbox_rect.center = offset_rect.center
                        pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
                        target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                        pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
