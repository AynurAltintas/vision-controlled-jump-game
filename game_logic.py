import random
import pygame
from pathlib import Path

class Player:
    def __init__(self):
        self.x = 100
        self.y = 250
        self.velocity = 0
        self.gravity = 0.5
        self.jump_force = -8
        self.size = 30

        assets_dir = Path(__file__).resolve().parent / "Assets" / "bird"
        self.frames = [
            pygame.image.load(str(assets_dir / "bird_0.png")).convert_alpha(),
            pygame.image.load(str(assets_dir / "bird_1.png")).convert_alpha(),
            pygame.image.load(str(assets_dir / "bird_2.png")).convert_alpha(),
            pygame.image.load(str(assets_dir / "bird_3.png")).convert_alpha(),
        ]
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.frames[0]

        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, jump=False):
        if jump:
            self.jump()
        self.velocity += self.gravity
        self.y += self.velocity

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
    
    def jump(self):
        self.velocity = self.jump_force

    def get_rect(self):
        return (self.x, int(self.y), self.size, self.size)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 60
        self.gap = 150
        self.top_height = random.randint(50, 300)
        self.speed = 4
        self.passed = False

    def update(self):
        self.x -= self.speed

    def off_screen(self):
        return self.x + self.width < 0

    def get_rects(self, screen_height):
        top_rect = (self.x, 0, self.width, self.top_height)
        bottom_rect = (
            self.x,
            self.top_height + self.gap,
            self.width,
            screen_height - (self.top_height + self.gap)
        )
        return top_rect, bottom_rect