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
