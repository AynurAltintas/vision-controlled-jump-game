import pygame
import cv2
import math
from game_logic import Player, Pipe
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from pathlib import Path

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

try:
    def draw_text_with_shadow(
        surface,
        text,
        font,
        color,
        position,
        shadow_color=(8, 12, 18),
        shadow_offset=(2, 2),
        center=False,
    ):
        shadow_surface = font.render(text, True, shadow_color)
        text_surface = font.render(text, True, color)

        if center:
            shadow_rect = shadow_surface.get_rect(
                center=(position[0] + shadow_offset[0], position[1] + shadow_offset[1])
            )
            text_rect = text_surface.get_rect(center=position)
        else:
            shadow_rect = shadow_surface.get_rect(
                topleft=(position[0] + shadow_offset[0], position[1] + shadow_offset[1])
            )
            text_rect = text_surface.get_rect(topleft=position)

        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)


    def draw_score_panel(surface, font, score, best_score):
        draw_text_with_shadow(
            surface,
            f"Skor: {score}",
            font,
            (244, 248, 252),
            (14, 12),
        )
        draw_text_with_shadow(
            surface,
            f"En iyi: {best_score}",
            font,
            (190, 228, 246),
            (14, 40),
        )

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
    font = pygame.font.SysFont("Segoe UI", 72, bold=True)
    title_font = pygame.font.SysFont("Segoe UI", 70, bold=True)
    subtitle_font = pygame.font.SysFont("Segoe UI", 44, bold=True)
    small_font = pygame.font.SysFont("Segoe UI", 36)
    tiny_font = pygame.font.SysFont("Segoe UI", 26)

    player = Player()
    pipes = [Pipe(800)]
    spawn_timer = 0
    score = 0
    death_timer = 0
    best_score = 0

    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    detector = GestureDetector()

    running = True
    prev_jump_detected = False
    prev_start_detected = False
    app_start_time = pygame.time.get_ticks()
    start_ready_delay_ms = 1500

    while running:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame, landmarks = tracker.process_frame(frame)

        jump_detected = detector.is_hand_open(landmarks)
        one_finger_detected = detector.is_one_finger(landmarks)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 

        # START EKRANI
        if game_state == "START":
            now = pygame.time.get_ticks()
            is_preparing = now - app_start_time < start_ready_delay_ms

            screen.blit(background_image, (0, 0))

            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((8, 12, 18, 80))
            screen.blit(overlay, (0, 0))

            draw_text_with_shadow(
                screen,
                "Vision Jump",
                title_font,
                (240, 248, 255),
                (400, 60),
                center=True,
            )

            if is_preparing:
                dot_count = (now // 300) % 3 + 1
                draw_text_with_shadow(
                    screen,
                    f"Kamera hazırlanıyor{'.' * dot_count}",
                    tiny_font,
                    (220, 235, 245),
                    (400, 112),
                    center=True,
                )
            else:
                pulse = (now // 350) % 2 == 0
                cta_color = (235, 248, 255) if pulse else (170, 215, 238)
                draw_text_with_shadow(
                    screen,
                    "Bir parmak çıkar ve başla",
                    subtitle_font,
                    cta_color,
                    (400, 112),
                    center=True,
                )

            status_text = "Algılandı" if one_finger_detected else "Jest bekleniyor"
            status_color = (75, 240, 160) if one_finger_detected else (255, 190, 120)
            draw_text_with_shadow(
                screen,
                status_text,
                tiny_font,
                status_color,
                (400, 152),
                center=True,
            )

            draw_text_with_shadow(
                screen,
                f"En iyi skor: {best_score}",
                tiny_font,
                (215, 230, 242),
                (22, 20),
            )

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (170, 120))
            camera_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            screen.blit(camera_surface, (610, 460))
            pygame.draw.rect(screen, (220, 235, 245), (610, 460, 170, 120), 2)
            
            if not is_preparing and one_finger_detected and not prev_start_detected:
                game_state = "PLAYING"
                prev_jump_detected = jump_detected

            prev_start_detected = one_finger_detected

            player.y = 265 + int(12 * math.sin(now / 220))
            player.velocity = 0
            player.idle()

            bird_scale = 2.4
            bird_image = pygame.transform.smoothscale(
                player.image,
                (
                    int(player.image.get_width() * bird_scale),
                    int(player.image.get_height() * bird_scale),
                ),
            )
            bird_angle = int(6 * math.sin(now / 260))
            bird_rotated = pygame.transform.rotate(bird_image, bird_angle)
            bird_rect = bird_rotated.get_rect(center=(400, 320 + int(10 * math.sin(now / 240))))
            screen.blit(bird_rotated, bird_rect)
            
            pygame.display.update()
            clock.tick(60)
            continue
        # OYUN EKRANI
        if game_state == "PLAYING":
            screen.blit(background_image, (0, 0))

            draw_score_panel(screen, tiny_font, score, best_score)

            if jump_detected and not prev_jump_detected:
                player.jump()
            prev_jump_detected = jump_detected

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
                    if score > best_score:
                        best_score = score

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

            draw_score_panel(screen, tiny_font, score, best_score)

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
            screen.blit(background_image, (0, 0))

            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((8, 12, 18, 90))
            screen.blit(overlay, (0, 0))

            pulse = (pygame.time.get_ticks() // 350) % 2 == 0
            restart_color = (240, 248, 255) if pulse else (170, 215, 238)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (170, 120))
            camera_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            screen.blit(camera_surface, (610, 460))
            pygame.draw.rect(screen, (220, 235, 245), (610, 460, 170, 120), 2)

            draw_text_with_shadow(
                screen,
                "Oyun Bitti!",
                font,
                (255, 178, 77),
                (400, 90),
                center=True,
            )
            draw_text_with_shadow(
                screen,
                f"Skor: {score}",
                small_font,
                (245, 248, 252),
                (400, 205),
                center=True,
            )
            draw_text_with_shadow(
                screen,
                f"En iyi: {best_score}",
                small_font,
                (245, 248, 252),
                (400, 245),
                center=True,
            )

            status_text = "Algılandı" if one_finger_detected else "Jest bekleniyor"
            status_color = (75, 240, 160) if one_finger_detected else (255, 190, 120)
            draw_text_with_shadow(
                screen,
                status_text,
                tiny_font,
                status_color,
                (400, 305),
                center=True,
            )
            draw_text_with_shadow(
                screen,
                "Bir parmak çıkararak tekrar başla",
                small_font,
                restart_color,
                (400, 365),
                center=True,
            )

            if one_finger_detected and not prev_start_detected:
                player = Player()
                pipes = [Pipe(800)]
                spawn_timer = 0
                score = 0
                death_timer = 0
                game_state = "PLAYING"
                prev_jump_detected = jump_detected
            
            prev_start_detected = one_finger_detected
            
            pygame.display.update()
            clock.tick(60)
            continue
except Exception as e:
    print("Bir hata oluştu:", e)
finally:
    cap.release()
    pygame.quit()   