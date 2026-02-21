import pygame
import cv2
from game_logic import Player, Pipe
from hand_tracker import HandTracker
from gesture_detector import GestureDetector

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

player = Player()
pipes = [Pipe(800)]
spawn_timer = 0
score = 0

cap = cv2.VideoCapture(0)
tracker = HandTracker()
detector = GestureDetector()

running = True
started = False
prev_hand_open = False

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # === UPDATE ===
    jump = False
    success, frame = cap.read()
    if success:
        frame = cv2.flip(frame, 1)
        _, landmarks = tracker.process_frame(frame)

        if not started:
            started = detector.is_fist(landmarks)
        else:
            hand_open = detector.is_hand_open(landmarks)
            jump = hand_open and not prev_hand_open
            prev_hand_open = hand_open

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, screen.get_size())
        camera_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        screen.blit(camera_surface, (0, 0))
    else:
        screen.fill((30, 30, 30))

    if started:
        player.update(jump)
    else:
        pygame.draw.rect(screen, (255, 255, 0), player.get_rect())
        font = pygame.font.SysFont(None, 32)
        text = font.render("Avuç kapat: Başla", True, (255, 255, 255))
        screen.blit(text, (20, 20))

    spawn_timer += 1
    if spawn_timer > 90:
        pipes.append(Pipe(800))
        spawn_timer = 0

    for pipe in pipes:
        pipe.update()

    pipes = [p for p in pipes if not p.off_screen()]

    # === DRAW PLAYER ===
    pygame.draw.rect(screen, (255, 255, 0), player.get_rect())

    # === DRAW PIPES ===
    for pipe in pipes:
        top_rect, bottom_rect = pipe.get_rects(600)
        pygame.draw.rect(screen, (0, 255, 0), top_rect)
        pygame.draw.rect(screen, (0, 255, 0), bottom_rect)

        # Collision
        if pygame.Rect(player.get_rect()).colliderect(top_rect) or \
           pygame.Rect(player.get_rect()).colliderect(bottom_rect):
            running = False

    # Yere düşme kontrolü
    if player.y + player.size >= 600:
        running = False

    # Ekranın üstüne çıkma kontrolü
    if player.y <= 0:
        running = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
cap.release()
cv2.destroyAllWindows()