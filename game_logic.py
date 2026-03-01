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

        self.state = "alive"
        self.scale = 1.25

        assets_dir = Path(__file__).resolve().parent / "Assets" / "bird"
        self.frames = [
            pygame.image.load(str(assets_dir / "bird_0.png")).convert_alpha(),
            pygame.image.load(str(assets_dir / "bird_1.png")).convert_alpha(),
            pygame.image.load(str(assets_dir / "bird_2.png")).convert_alpha(),
            pygame.image.load(str(assets_dir / "bird_3.png")).convert_alpha(),
        ]
        self.frames = [
            pygame.transform.smoothscale(
                frame,
                (
                    int(frame.get_width() * self.scale),
                    int(frame.get_height() * self.scale),
                ),
            )
            for frame in self.frames
        ]
        self.fly_frames = self.frames
        death_dir = Path(__file__).resolve().parent / "Assets" / "death"

        self.death_frames = [
            pygame.image.load(str(death_dir / "death_0.png")).convert_alpha(),
            pygame.image.load(str(death_dir / "death_1.png")).convert_alpha(),
            pygame.image.load(str(death_dir / "death_2.png")).convert_alpha(),
        ]
        self.death_frames = [
            pygame.transform.smoothscale(
                frame,
                (
                    int(frame.get_width() * self.scale),
                    int(frame.get_height() * self.scale),
                ),
            )
            for frame in self.death_frames
        ]

        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.frames[0]

        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, jump=False):
        if self.state == "alive":

            if jump:
                self.jump()

            self.velocity += self.gravity
            self.y += self.velocity

            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.fly_frames):
                self.frame_index = 0

            self.image = self.fly_frames[int(self.frame_index)]

        elif self.state == "dying":
            self.velocity += self.gravity
            self.y += self.velocity

            self.frame_index += 0.15

            if self.frame_index >= len(self.death_frames):
                self.frame_index = len(self.death_frames) - 1
                self.state = "dead"

            self.image = self.death_frames[int(self.frame_index)]

        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def jump(self):
        if self.state == "alive":
            self.velocity = self.jump_force
    
    def die(self):
        if self.state == "alive":
            self.state = "dying"
            self.frame_index = 0
            self.velocity = 0

    def get_rect(self):
        return pygame.Rect(self.x, int(self.y), self.width, self.height)    
class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap = 150
        self.top_height = random.randint(50, 300)
        self.speed = 4
        self.passed = False

        assets_dir = Path(__file__).resolve().parent / "Assets" / "pipes"

        self.top_image = pygame.image.load(
            str(assets_dir / "pipe_top.png")
        ).convert_alpha()

        self.bottom_image = pygame.image.load(
            str(assets_dir / "pipe_bottom.png")
        ).convert_alpha()

        top_bounds = self.top_image.get_bounding_rect()
        if top_bounds.width > 0 and top_bounds.height > 0:
            self.top_image = self.top_image.subsurface(top_bounds).copy()

        bottom_bounds = self.bottom_image.get_bounding_rect()
        if bottom_bounds.width > 0 and bottom_bounds.height > 0:
            self.bottom_image = self.bottom_image.subsurface(bottom_bounds).copy()

        base_width = max(self.top_image.get_width(), self.bottom_image.get_width())
        self.width = int(base_width * 1.50)

        self._cache_screen_height = None
        self._top_scaled = None
        self._bottom_scaled = None
        self._top_mask = None
        self._bottom_mask = None
        self._top_visible_bounds = None
        self._bottom_visible_bounds = None

    def _ensure_cache(self, screen_height):
        if self._cache_screen_height == screen_height:
            return

        bottom_height = max(1, screen_height - (self.top_height + self.gap))

        self._top_scaled = pygame.transform.smoothscale(
            self.top_image,
            (self.width, self.top_height)
        )
        self._bottom_scaled = pygame.transform.smoothscale(
            self.bottom_image,
            (self.width, bottom_height)
        )

        self._top_mask = pygame.mask.from_surface(self._top_scaled)
        self._bottom_mask = pygame.mask.from_surface(self._bottom_scaled)

        self._top_visible_bounds = self._top_scaled.get_bounding_rect()
        self._bottom_visible_bounds = self._bottom_scaled.get_bounding_rect()

        self._cache_screen_height = screen_height

    def draw(self, screen, screen_height):
        self._ensure_cache(screen_height)
        screen.blit(self._top_scaled, (self.x, 0))
        screen.blit(self._bottom_scaled, (self.x, self.top_height + self.gap))

    def update(self):
        self.x -= self.speed

    def off_screen(self):
        return self.x + self.width < 0

    def get_rects(self, screen_height):
        self._ensure_cache(screen_height)
        top_rect = self._top_visible_bounds.move(int(self.x), 0)
        bottom_rect = self._bottom_visible_bounds.move(int(self.x), self.top_height + self.gap)
        return top_rect, bottom_rect

    def collides_with(self, player_surface, player_pos, screen_height):
        self._ensure_cache(screen_height)

        player_mask = pygame.mask.from_surface(player_surface)
        player_x, player_y = int(player_pos[0]), int(player_pos[1])

        top_offset = (int(self.x) - player_x, -player_y)
        bottom_offset = (
            int(self.x) - player_x,
            int(self.top_height + self.gap) - player_y,
        )

        if player_mask.overlap(self._top_mask, top_offset):
            return True

        if player_mask.overlap(self._bottom_mask, bottom_offset):
            return True

        return False