import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Endless Runner")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Clock and FPS
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.Font(None, 48)

# Load assets
player_image = pygame.Surface((50, 50))
player_image.fill(BLUE)
obstacle_image = pygame.Surface((50, 50))
obstacle_image.fill(RED)
overhead_obstacle_image = pygame.Surface((50, 50))  # Taller overhead obstacle
overhead_obstacle_image.fill(RED)
background_color = (135, 206, 250)  # Sky blue

# Game variables
player_x, player_y = 100, SCREEN_HEIGHT - 100
player_velocity = 0
gravity = 0.5
is_jumping = False
is_ducking = False

obstacle_speed = 6  # Initial speed
obstacle_list = []

background_scroll = 0

game_active = False
score = 0
last_obstacle_time = 0  # Time since the last obstacle was spawned
game_start_time = 0  # Time when the game started

# Define the maximum speed limit for obstacles
MAX_OBSTACLE_SPEED = 12  # Maximum speed the obstacles can have

# Functions
def display_message(text, color, y_offset=0):
    """Display centered message on the screen."""
    message = font.render(text, True, color)
    rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(message, rect)

def reset_game():
    """Reset game variables."""
    global player_x, player_y, player_velocity, is_jumping, is_ducking, obstacle_list, game_active, score, last_obstacle_time, obstacle_speed, game_start_time
    player_x, player_y = 100, SCREEN_HEIGHT - 100
    player_velocity = 0
    is_jumping = False
    is_ducking = False
    obstacle_list.clear()
    score = 0
    last_obstacle_time = pygame.time.get_ticks()
    obstacle_speed = 6  # Reset speed
    game_start_time = pygame.time.get_ticks()  # Reset the game start time
    game_active = True

def move_obstacles(obstacles):
    """Move obstacles and remove them if off-screen."""
    for obstacle in obstacles:
        obstacle['x'] -= obstacle_speed
    return [obs for obs in obstacles if obs['x'] > -50]

def check_collision(obstacles):
    """Check for collisions between the player and obstacles."""
    player_rect = pygame.Rect(player_x, player_y + 25, 50, 25) if is_ducking else pygame.Rect(player_x, player_y, 50, 50)
    for obs in obstacles:
        obs_rect = pygame.Rect(obs['x'], obs['y'], obs['width'], obs['height'])
        if player_rect.colliderect(obs_rect):
            return True
    return False

def spawn_obstacle():
    """Spawn an obstacle at a random position."""
    global last_obstacle_time
    current_time = pygame.time.get_ticks()

    # Calculate time passed since the game started
    time_elapsed = current_time - game_start_time
    # Every 10 seconds (10000ms), reduce the spawn interval by 100ms, but cap it at 500ms
    spawn_interval = max(700, 1000 - (time_elapsed // 15000) * 100)

    if current_time - last_obstacle_time > spawn_interval:  # Spawn obstacles based on dynamic interval
        obstacle_type = random.choice(["ground", "overhead"])

        if obstacle_type == "ground":
            obstacle_list.append({'x': SCREEN_WIDTH, 'y': SCREEN_HEIGHT - 100, 'width': 50, 'height': 50})
        else:
            obstacle_list.append({'x': SCREEN_WIDTH, 'y': SCREEN_HEIGHT - 140, 'width': 50, 'height': 50})
        
        last_obstacle_time = current_time

# Main loop
running = True
while running:
    screen.fill(background_color)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Start menu
        if not game_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                reset_game()

        # Player input
        if game_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_jumping:
                    player_velocity = -10
                    is_jumping = True
                if event.key == pygame.K_DOWN:
                    is_ducking = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    is_ducking = False

    if game_active:
        # Background scrolling
        background_scroll -= 2
        if background_scroll <= -SCREEN_WIDTH:
            background_scroll = 0
        
        pygame.draw.rect(screen, (100, 100, 255), (background_scroll, 0, SCREEN_WIDTH * 2, SCREEN_HEIGHT))
        
        # Player gravity and movement
        player_velocity += gravity
        player_y += player_velocity
        if player_y >= SCREEN_HEIGHT - 100:
            player_y = SCREEN_HEIGHT - 100
            is_jumping = False
        
        # Spawn and move obstacles
        spawn_obstacle()
        obstacle_list = move_obstacles(obstacle_list)
        
        # Increase the obstacle speed based on score, but apply the max speed limit
        obstacle_speed = min(6 + (score // 300), MAX_OBSTACLE_SPEED)
        
        # Draw obstacles
        for obs in obstacle_list:
            obstacle_img = obstacle_image if obs['y'] == SCREEN_HEIGHT - 100 else overhead_obstacle_image
            screen.blit(obstacle_img, (obs['x'], obs['y']))
        
        # Collision detection
        if check_collision(obstacle_list):
            game_active = False

        # Draw player
        if is_ducking:
            pygame.draw.rect(screen, BLUE, (player_x, player_y + 25, 50, 25))  # Smaller rectangle while ducking
        else:
            screen.blit(player_image, (player_x, player_y))

        # Update score
        score += 1
        score_text = font.render(f"Score: {score // 10}", True, BLACK)  # Divide by 10 for a slower score increment
        screen.blit(score_text, (10, 10))
    else:
        # Start menu or game over screen
        display_message("Game Over!" if obstacle_list else "Click to Play", BLACK)
        display_message("Try Again", RED, y_offset=50)
        display_message(f"Score: {score // 10}", BLACK, y_offset=100)

    # Update the screen
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
