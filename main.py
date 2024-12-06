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

# Player size for hitbox
player_width = 50
player_height = 50

# Load and resize assets
obstacle_image = pygame.image.load("log.png").convert_alpha()  # Your ground obstacle sprite
obstacle_image = pygame.transform.scale(obstacle_image, (60, 50))  # Resize log

overhead_obstacle_image = pygame.image.load("bird.png").convert_alpha()  # Overhead obstacle sprite
overhead_obstacle_image = pygame.transform.scale(overhead_obstacle_image, (60, 50))  # Resize bird (adjust size as necessary)

background_image = pygame.image.load("background.png").convert_alpha()

# Scale the background to fit the screen width and adjust height to maintain aspect ratio
background_width, background_height = background_image.get_size()
aspect_ratio = background_height / background_width
scaled_background_height = int(SCREEN_WIDTH * aspect_ratio)
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, scaled_background_height))

# Load character sprites for running animation and resize them to fit the player hitbox
player_running_sprites = [
    pygame.transform.scale(pygame.image.load("run__000.png").convert_alpha(), (player_width, player_height)),
    pygame.transform.scale(pygame.image.load("run__001.png").convert_alpha(), (player_width, player_height)),
    pygame.transform.scale(pygame.image.load("run__002.png").convert_alpha(), (player_width, player_height)),
    pygame.transform.scale(pygame.image.load("run__003.png").convert_alpha(), (player_width, player_height))
]

# Load jumping sprite (resize to player size)
player_jumping_sprite = pygame.transform.scale(pygame.image.load("jump__003.png").convert_alpha(), (player_width, player_height))

# Load ducking sprite
player_duck_sprite = pygame.transform.scale(pygame.image.load("slide__000.png").convert_alpha(), (player_width, player_height))

# Game variables
player_x, player_y = 100, SCREEN_HEIGHT - 100
player_velocity = 0
gravity = 0.5
is_jumping = False
is_ducking = False
current_sprite = 0  # Tracks the frame of the running animation
animation_speed = 0.2  # Adjust speed of animation

obstacle_speed = 6  # Initial speed
obstacle_list = []
MAX_OBSTACLE_SPEED = 13  # Maximum obstacle speed

background_scroll = 0

game_active = False
score = 0
last_obstacle_time = 0  # Time since the last obstacle was spawned
game_start_time = 0  # Time when the game started

# Functions
def display_message(text, color, y_offset=0):
    """Display centered message on the screen."""
    message = font.render(text, True, color)
    rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(message, rect)

def reset_game():
    """Reset game variables."""
    global player_x, player_y, player_velocity, is_jumping, is_ducking, obstacle_list, game_active, score, last_obstacle_time, obstacle_speed, game_start_time, background_scroll
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
    background_scroll = 0  # Reset background scroll position

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
    # Every 10 seconds (10000ms), reduce the spawn interval by 100ms
    spawn_interval = max(700, 1000 - (time_elapsed // 15000) * 100)

    if current_time - last_obstacle_time > spawn_interval:  # Spawn obstacles based on dynamic interval
        obstacle_type = random.choice(["ground", "overhead"])

        if obstacle_type == "ground":
            obstacle_list.append({'x': SCREEN_WIDTH, 'y': SCREEN_HEIGHT - 100, 'width': 60, 'height': 50})  # Resize to log size
        else:
            obstacle_list.append({'x': SCREEN_WIDTH, 'y': SCREEN_HEIGHT - 140, 'width': 60, 'height': 50})  # Resize to bird size
        
        last_obstacle_time = current_time

def update_animation():
    """Update the player's running animation."""
    global current_sprite
    current_sprite += animation_speed
    if current_sprite >= len(player_running_sprites):
        current_sprite = 0

# Main loop
running = True
while running:
    screen.fill((135, 206, 250))  # Set background to sky blue
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Quit the game if the close button is clicked
        
        # Start menu
        if not game_active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Check if the user clicks "Try Again" button
                if SCREEN_HEIGHT // 2 + 50 < mouse_y < SCREEN_HEIGHT // 2 + 100:  # "Try Again"
                    reset_game()
                # Check if the user clicks the "Quit" button
                elif SCREEN_HEIGHT // 2 + 100 < mouse_y < SCREEN_HEIGHT // 2 + 150:  # "Quit"
                    running = False

        # Player input
        if game_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_jumping and not is_ducking:
                    player_velocity = -10
                    is_jumping = True
                if event.key == pygame.K_DOWN and not is_jumping:
                    is_ducking = True
                if event.key == pygame.K_ESCAPE:  # Escape key to quit the game
                    running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    is_ducking = False

    if game_active:
        # Background scrolling
        background_scroll -= 2
        if background_scroll <= -SCREEN_WIDTH:
            background_scroll = 0
        
        # Draw the background image twice to create the scrolling effect
        screen.blit(background_image, (background_scroll, SCREEN_HEIGHT - background_image.get_height()))  # Draw the first background image at the bottom
        screen.blit(background_image, (background_scroll + SCREEN_WIDTH, SCREEN_HEIGHT - background_image.get_height()))  # Draw the second background image

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
        
        # Draw obstacles using the sprite images
        for obs in obstacle_list:
            obstacle_img = obstacle_image if obs['y'] == SCREEN_HEIGHT - 100 else overhead_obstacle_image
            screen.blit(obstacle_img, (obs['x'], obs['y']))
        
        # Collision detection
        if check_collision(obstacle_list):
            game_active = False

        # Update and draw player
        if is_jumping:
            screen.blit(player_jumping_sprite, (player_x, player_y))
        elif is_ducking:
            screen.blit(player_duck_sprite, (player_x, player_y))
        else:
            update_animation()
            screen.blit(player_running_sprites[int(current_sprite)], (player_x, player_y))

        # Update score
        score += 1
        score_text = font.render(f"Score: {score // 10}", True, WHITE)  # Divide by 10 for a slower score increment
        screen.blit(score_text, (10, 10))
    else:
        # Game over screen with quit button
        display_message("Game Over!" if obstacle_list else "Welcome!", BLACK)
        display_message("Click to Play", RED, y_offset=50)
        display_message(f"Score: {score // 10}", BLACK, y_offset=100)
        
        # Draw quit button
        quit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50)
        display_message("Quit", WHITE, y_offset=150)

    # Update the screen
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

display_message("Game Over!" if obstacle_list else "Welcome!", BLACK)