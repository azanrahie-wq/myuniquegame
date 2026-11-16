import pygame
import random
import os

try:
    os.chdir(os.path.dirname(os.path.abspath(_file_)))
except:
    pass

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Epic 2D Adventure Platformer")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

# تصویریں لوڈ کرنے کا محفوظ طریقہ
def load_image(filename, fallback_color, size):
    if os.path.exists(filename):
        try:
            img = pygame.image.load(filename)
            return pygame.transform.scale(img, size)
        except:
            pass
    surf = pygame.Surface(size)
    surf.fill(fallback_color)
    return surf

bg_img = load_image('background.jpg.jpg', (20, 30, 60), (SCREEN_WIDTH, SCREEN_HEIGHT))
player_img = load_image('player.jpg.jpg', (0, 255, 0), (45, 55))
enemy_img = load_image('enemy.jpg.jpg', (255, 0, 0), (40, 40))

# گیم کے ویری ایبلز کو ری سیٹ کرنے کا فنکشن
def reset_game():
    global player_x, player_y, player_vel_y, is_jumping, score, level, lives, enemies, bullets, enemies_defeated, enemy_spawn_timer
    player_x = 100
    player_y = 420
    player_vel_y = 0
    is_jumping = False
    score = 0
    level = 1
    lives = 3
    enemies = []
    bullets = []
    enemies_defeated = 0
    enemy_spawn_timer = 0

reset_game()
game_over = False
victory = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # چھلانگ لگانے کے لیے SPACE دبائیں
            if event.key == pygame.K_SPACE and not is_jumping:
                player_vel_y = -14
                is_jumping = True
            
            # گولی چلانے کے لیے 'F' دبائیں
            if event.key == pygame.K_f and not game_over and not victory:
                bullets.append({'x': player_x + 45, 'y': player_y + 20, 'speed': 10})

            # گیم اوور یا جیتنے پر 'R' دبا کر دوبارہ شروع کریں
            if (game_over or victory) and event.key == pygame.K_r:
                reset_game()
                game_over = False
                victory = False

    if not game_over and not victory:
        # کی بورڈ کنٹرولز (دائیں اور بائیں چلنا)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= 5
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - 50:
            player_x += 5

        # گریویٹی (زمین پر واپس لانا)
        player_vel_y += 0.6
        player_y += player_vel_y

        # زمین کی حد (Ground Level)
        ground_y = 420
        if player_y >= ground_y:
            player_y = ground_y
            player_vel_y = 0
            is_jumping = False

        # لیول کے حساب سے دشمنوں کا آنا
        enemy_spawn_timer += 1
        spawn_interval = max(30, 80 - (level * 10))
        if enemy_spawn_timer >= spawn_interval and len(enemies) < (2 + level):
            enemies.append({'x': 800, 'y': 430, 'speed': 2 + level})
            enemy_spawn_timer = 0

        # دشمنوں کی حرکت
        for enemy in enemies[:]:
            enemy['x'] -= enemy['speed']
            if enemy['x'] < -50:
                enemies.remove(enemy)

        # گولیوں کی حرکت
        for bullet in bullets[:]:
            bullet['x'] += bullet['speed']
            if bullet['x'] > SCREEN_WIDTH:
                bullets.remove(bullet)

        # ہیرو کی گولی اور دشمن کی ٹکر
        for bullet in bullets[:]:
            b_rect = pygame.Rect(bullet['x'], bullet['y'], 12, 6)
            for enemy in enemies[:]:
                e_rect = pygame.Rect(enemy['x'], enemy['y'], 40, 40)
                if b_rect.colliderect(e_rect):
                    if bullet in bullets: bullets.remove(bullet)
                    if enemy in enemies: enemies.remove(enemy)
                    score += 15
                    enemies_defeated += 1
                    break

        # ہیرو اور دشمن کی ٹکر
        player_rect = pygame.Rect(player_x, player_y, 45, 55)
        for enemy in enemies[:]:
            e_rect = pygame.Rect(enemy['x'], enemy['y'], 40, 40)
            if player_rect.colliderect(e_rect):
                lives -= 1
                enemies.remove(enemy)
                if lives <= 0:
                    game_over = True

        # لیول اپ گریڈ سسٹم (کل 5 لیولز)
        required_kills = 4 * level
        if enemies_defeated >= required_kills:
            level += 1
            enemies_defeated = 0
            if level > 5:
                victory = True

    # سکرین پر چیزیں ڈرا کرنا
    screen.blit(bg_img, (0, 0))

    # نیچے دریا/پانی اور زمین کا منظر
    pygame.draw.rect(screen, (30, 100, 200), (0, 475, SCREEN_WIDTH, 125))  # نیلے رنگ کا دریا
    pygame.draw.rect(screen, (80, 60, 40), (0, 470, SCREEN_WIDTH, 10))    # زمینی پٹی

    # ہیرو اور دشمنوں کو دکھانا
    screen.blit(player_img, (player_x, player_y))
    for enemy in enemies:
        screen.blit(enemy_img, (enemy['x'], enemy['y']))

    # ہیرو کی گولیاں دکھانا
    for bullet in bullets:
        pygame.draw.rect(screen, (255, 255, 0), (bullet['x'], bullet['y'], 12, 6))

    # اسکور، لیول (1 سے 5) اور لائفز دکھانا
    info_text = font.render(f"Score: {score}  |  Adventure Level: {level}/5  |  Lives: {lives}", True, (255, 255, 255))
    screen.blit(info_text, (20, 20))

    # کنٹرولز کی ہدایات
    instructions = font.render("Move: Left/Right | Jump: SPACE | Shoot: F", True, (200, 200, 200))
    screen.blit(instructions, (20, 560))

    # اگر گیم اوور ہو جائے
    if game_over:
        over_text = font.render("GAME OVER! Press 'R' to Restart", True, (255, 0, 0))
        screen.blit(over_text, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2))

    # اگر تمام 5 لیولز جیت جائیں
    if victory:
        win_text = font.render("VICTORY! You Crossed All Adventure Levels!", True, (0, 255, 0))
        screen.blit(win_text, (SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()