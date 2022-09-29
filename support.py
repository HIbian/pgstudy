from os import walk
import pygame


def import_folder(path):
    surface_list = []

    # walk(path) returns an array which contains objects of 3 group,we only need the last.
    for _, __, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    return surface_list
