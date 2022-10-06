from pygame.math import Vector2

# game information
GAME_NAME = 'hibian\'s practice'
GAME_VERSION = '0.0.1'

# screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64

# overlay positions
OVERLAY_POSITIONS = {
    'tool': (40, SCREEN_HEIGHT - 15),
    'seed': (100, SCREEN_HEIGHT - 15)
}

LAYERS = {
    'water': 0,
    'ground': 1,
    'soil': 2,
    'soil water': 3,
    'rain floor': 4,
    'house bottom': 5,
    'ground plant': 6,
    'main': 7,
    'house top': 8,
    'fruit': 9,
    'rain drops': 10
}
