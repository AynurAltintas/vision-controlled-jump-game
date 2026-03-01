import pygame
import cv2
from game_logic import Player, Pipe
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from pathlib import Path

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

assets_dir = Path(__file__).resolve().parent / "Assets" / "background"
background_path = None
for candidate in ("background.png", "bg.png", "background.jpg", "bg.jpg"):
    candidate_path = assets_dir / candidate
    if candidate_path.exists():
        background_path = candidate_path
        break

if background_path is not None:
    background_image = pygame.image.load(str(background_path)).convert()
    background_image = pygame.transform.scale(background_image, (800, 600))
else:
    background_image = pygame.Surface((800, 600))
    background_image.fill((30, 40, 60))

game_state = "START"
font = pygame.font.SysFont(None, 70)
small_font = pygame.font.SysFont(None, 40)

player = Player()
pipes = [Pipe(800)]
spawn_timer = 0
score = 0
death_timer = 0

cap = cv2.VideoCapture(0)
tracker = HandTracker()
detector = GestureDetector()

running = True
started = False
prev_hand_open = False

while running:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame, landmarks = tracker.process_frame(frame)

    jump_detected = detector.is_hand_open(landmarks)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 

    # START EKRANI
    if game_state == "START":
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (800, 600))
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        screen.blit(frame_surface, (0, 0))
        
        title = font.render("Görsel Kontrollü Zıplama Oyunu", True, (255, 255, 255))
        info = small_font.render("Avuç aç: Zıpla | Avucunu açarak başla", True, (200, 200, 200))

        screen.blit(title, (200, 200))
        screen.blit(info, (220, 300))
        
        if jump_detected:
            game_state = "PLAYING"
        
        pygame.display.update()
        clock.tick(60)
        continue
    # OYUN EKRANI
    if game_state == "PLAYING":
        screen.blit(background_image, (0, 0))

        score_bg = pygame.Surface((140, 40))
        score_bg.set_alpha(150)
        score_bg.fill((0, 0, 0))
        screen.blit(score_bg, (5, 5))

        score_text = small_font.render(f"Skor: {score}", True, (255, 255, 255))
        screen.blit(score_text, (15, 10))   

        if jump_detected and not prev_hand_open:    
            player.jump()
        prev_hand_open = jump_detected

        player.update()

        spawn_timer += 1
        if spawn_timer > 90:
            pipes.append(Pipe(800))
            spawn_timer = 0
        
        for pipe in pipes:
            pipe.update()
        pipes = [p for p in pipes if not p.off_screen()]    

        player_rect = pygame.Rect(
            player.x,
            int(player.y),
            player.image.get_width(),
            player.image.get_height(),
        )
        #kuşun dönme efekti
        bird_angle = max(-35, min(25, -player.velocity * 4))
        rotated_bird = pygame.transform.rotate(player.image, bird_angle)
        rotated_rect = rotated_bird.get_rect(center=player_rect.center)
        screen.blit(rotated_bird, rotated_rect.topleft)

        for pipe in pipes:
            pipe.draw(screen, 600)

            if pipe.collides_with(player.image, (player.x, player.y), 600):
                player.die()
                game_state = "DYING"
                death_timer = 0
            #skor kontrolü
            if not pipe.passed and pipe.x + pipe.width < player.x:
                pipe.passed = True
                score += 1

        # Kamera görüntüsünü küçültme ve sağ alt köşeye yerleştirme
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (200, 150))
        camera_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))

        screen.blit(camera_surface, (800 - 210, 600 - 160))
        pygame.draw.rect(screen, (255, 255, 255), (800 - 210, 600 - 160, 200, 150), 2)

        # Alt ve üst kenarlara çarpma kontrolü
        if player_rect.bottom >= 600:
            player.die()
            game_state = "DYING"
            death_timer = 0
        if player_rect.top <= 0:
            player.die()
            game_state = "DYING"
            death_timer = 0

        pygame.display.update()
        clock.tick(60)  
        continue
    # ÖLME ANİMASYONU EKRANI
    if game_state == "DYING":
        screen.blit(background_image, (0, 0))

        score_bg = pygame.Surface((140, 40))
        score_bg.set_alpha(150)
        score_bg.fill((0, 0, 0))
        screen.blit(score_bg, (5, 5))

        score_text = small_font.render(f"Skor: {score}", True, (255, 255, 255))
        screen.blit(score_text, (15, 10))

        for pipe in pipes:
            pipe.draw(screen, 600)

        player.update()
        player_rect = pygame.Rect(
            player.x,
            int(player.y),
            player.image.get_width(),
            player.image.get_height(),
        )
        bird_angle = max(-35, min(80, -player.velocity * 4))
        rotated_bird = pygame.transform.rotate(player.image, bird_angle)
        rotated_rect = rotated_bird.get_rect(center=player_rect.center)
        screen.blit(rotated_bird, rotated_rect.topleft)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (200, 150))
        camera_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        screen.blit(camera_surface, (800 - 210, 600 - 160))
        pygame.draw.rect(screen, (255, 255, 255), (800 - 210, 600 - 160, 200, 150), 2)

        death_timer += 1
        if player.state == "dead" or death_timer > 90:
            game_state = "GAME_OVER"

        pygame.display.update()
        clock.tick(60)
        continue
    # GAME OVER EKRANI
    if game_state == "GAME_OVER":
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = cv2.resize(frame_rgb, (800, 600))           
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        screen.blit(frame_surface, (0, 0))
        
        game_over_text = font.render("Oyun Bitti!", True, (255, 0, 0))
        restart_text = small_font.render("Avuç açarak tekrar başla", True, (255, 255, 255))
        score_text = small_font.render(f"Skor: {score}", True, (255, 255, 255))

        screen.blit(game_over_text, (220, 220))
        screen.blit(score_text, (350, 300))
        screen.blit(restart_text, (150, 320))

        if jump_detected:
            player = Player()
            pipes = [Pipe(800)]
            spawn_timer = 0
            score = 0
            death_timer = 0
            game_state = "PLAYING"
        
        prev_hand_open = jump_detected
        
        pygame.display.update()
        clock.tick(60)
        continue
cap.release()
pygame.quit()   