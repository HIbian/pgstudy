import pygame
from settings import *
from pytmx.util_pygame import load_pygame
from support import *
from random import choice


class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil']


class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = LAYERS['soil water']


class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered):
        super().__init__(groups)
        # setup
        self.plant_type = plant_type
        self.frames = import_folder(f'./graphics/fruit/{plant_type}')
        self.soil = soil
        self.check_watered = check_watered

        # plant growing
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[self.plant_type]
        self.harvestable = False

        # sprite setup
        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == 'corn' else -8
        self.rect = self.image.get_rect(midbottom=soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))
        self.z = LAYERS['ground plant']

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed

            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26, self.rect.height * 0.4)

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            # the image changed
            self.rect = self.image.get_rect(midbottom=self.soil.rect.midbottom + pygame.math.Vector2(0, self.y_offset))


class SoilLayer:
    def __init__(self, all_sprites, collision_sprites):
        # requirements
        # if the area is farm-able
        # if the soil has been watered
        # if the soil has plant

        # sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        # graphics
        self.soil_surfs = import_folder_dict('./graphics/soil/')
        self.water_surfs = import_folder('./graphics/soil_water/')

        self.create_soil_grid()
        self.create_hit_rects()

        # raining
        self.raining = False

    def create_soil_grid(self):
        # maintain a grid list of farm-able tiles.
        ground = pygame.image.load('./graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() // TILE_SIZE
        self.grid = [[[] for col in range(h_tiles)] for row in range(v_tiles)]
        for x, y, _ in load_pygame('./data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE
                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                    if self.raining:
                        self.water_all()

    def water(self, tartget_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(tartget_pos):
                # 1. add an entry to the soil grid -> 'w'
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                self.grid[y][x].append('W')
                # 2. create a water sprite
                # 2.1.copy the position from the soil sprite
                # 2.2. for the surface -> import the folder '../graphics/soil_water'
                # 2.3.randomly select on surface
                # 2.4.create one more group 'water_sprites'
                pos = soil_sprite.rect.topleft
                surf = choice(self.water_surfs)
                WaterTile(pos, surf, [self.all_sprites, self.water_sprites])

    def water_all(self):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    WaterTile((x, y), choice(self.water_surfs), [self.all_sprites, self.water_sprites])

    def remove_water(self):
        # destory all water sprites
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        # clean up the grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def check_watered(self, pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self, target_pos, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    Plant(seed, [self.all_sprites, self.collision_sprites, self.plant_sprites], soil_sprite,
                          self.check_watered)

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        # to change the shape of the old soil when a new soil is next to it.It means we need to redraw all the soil.
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell:

                    # tile options
                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]
                    tile_tpye = 'o'

                    # all sides
                    if all((t, r, b, l)): tile_tpye = 'x'
                    # horizontal tiles only
                    if l and not any((t, r, b)): tile_tpye = 'r'
                    if r and not any((t, l, b)): tile_tpye = 'l'
                    if r and l and not any((t, b)): tile_tpye = 'lr'
                    # vertical only
                    if b and not any((l, r, t)): tile_tpye = 't'
                    if t and not any((r, l, b)): tile_tpye = 'b'
                    if t and b and not any((r, l)): tile_tpye = 'tb'
                    # corners
                    if l and b and not any((t, r)): tile_tpye = 'tr'
                    if l and t and not any((b, r)): tile_tpye = 'br'
                    if r and b and not any((t, l)): tile_tpye = 'tl'
                    if r and t and not any((b, l)): tile_tpye = 'bl'
                    # T shapes
                    if all((t, b, r)) and not l: tile_tpye = 'tbr'
                    if all((t, b, l)) and not r: tile_tpye = 'tbl'
                    if all((t, l, r)) and not b: tile_tpye = 'lrb'
                    if all((l, b, r)) and not t: tile_tpye = 'lrt'

                    SoilTile(
                        pos=(index_col * TILE_SIZE, index_row * TILE_SIZE),
                        surf=self.soil_surfs[tile_tpye],
                        groups=[self.all_sprites, self.soil_sprites]
                    )
