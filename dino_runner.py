import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 350
FPS = 60

# Physics constants
GRAVITY = 1.0
JUMP_FORCE = -16
GAME_SPEED = 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DINO_COLOR = (83, 83, 83)  # Gray color for dinosaur
SKY_COLOR = (135, 206, 235)  # Light blue for sky
GROUND_COLOR = (210, 180, 140)  # Tan/sand color for desert
CACTUS_COLOR = (50, 120, 50)  # Dark green for cacti

# Power-up colors
SPEED_COLOR = (255, 165, 0)  # Orange for speed boost
POINTS_COLOR = (255, 215, 0)  # Gold for double points
SHIELD_COLOR = (0, 191, 255)  # Deep sky blue for invincibility

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Runner")
clock = pygame.time.Clock()

# Initialize font for score
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)
small_font = pygame.font.SysFont('Arial', 20)

# Dinosaur properties
dino_width = 60
dino_height = 80
dino_x = 100
dino_y = GROUND_HEIGHT - dino_height
dino_vel_y = 0
is_jumping = False
animation_count = 0

# Game variables
score = 0
obstacles = []
powerups = []
game_over = False

# Power-up effects
has_speed_boost = False
has_double_points = False
has_shield = False
speed_boost_timer = 0
double_points_timer = 0
shield_timer = 0
original_game_speed = GAME_SPEED

# Cloud properties
clouds = []
for i in range(3):
    clouds.append({
        'x': random.randint(0, SCREEN_WIDTH),
        'y': random.randint(50, 150),
        'width': random.randint(60, 120),
        'height': random.randint(30, 50),
        'speed': random.uniform(0.5, 1.5)
    })

# Function to draw the dinosaur with running animation
def draw_dinosaur(x, y, animation_frame):
    # Body
    body_color = DINO_COLOR
    
    # Change color if shield is active
    if has_shield:
        # Flashing effect for shield
        if pygame.time.get_ticks() % 500 < 250:
            body_color = SHIELD_COLOR
    
    # Body
    pygame.draw.rect(screen, body_color, (x, y + 20, 40, 40))
    
    # Neck and head
    pygame.draw.rect(screen, body_color, (x + 30, y, 30, 30))
    
    # Eye
    pygame.draw.circle(screen, WHITE, (x + 50, y + 10), 5)
    pygame.draw.circle(screen, BLACK, (x + 50, y + 10), 2)
    
    # Legs with animation
    leg_width = 8
    leg_height = 20
    
    if is_jumping:
        # Both legs forward when jumping
        pygame.draw.rect(screen, body_color, (x + 5, y + 60, leg_width, leg_height))
        pygame.draw.rect(screen, body_color, (x + 25, y + 60, leg_width, leg_height))
    else:
        # Alternate legs for running animation
        if animation_frame % 2 == 0:
            pygame.draw.rect(screen, body_color, (x + 5, y + 60, leg_width, leg_height))
            pygame.draw.rect(screen, body_color, (x + 25, y + 60 - 5, leg_width, leg_height))
        else:
            pygame.draw.rect(screen, body_color, (x + 5, y + 60 - 5, leg_width, leg_height))
            pygame.draw.rect(screen, body_color, (x + 25, y + 60, leg_width, leg_height))
    
    # Tail
    pygame.draw.polygon(screen, body_color, [(x, y + 30), (x - 20, y + 20), (x - 10, y + 40)])
    
    # Arm
    pygame.draw.rect(screen, body_color, (x + 25, y + 30, 15, 5))
    
    # Draw shield effect if active
    if has_shield:
        pygame.draw.circle(screen, SHIELD_COLOR, (x + 30, y + 40), 45, 2)

# Function to create a new cactus
def create_cactus():
    cactus_height = random.randint(40, 70)
    cactus_width = random.randint(15, 30)
    
    # Create a more complex cactus with branches
    cactus = {
        'x': SCREEN_WIDTH,
        'y': GROUND_HEIGHT - cactus_height,
        'width': cactus_width,
        'height': cactus_height,
        'passed': False,
        'branches': []
    }
    
    # Add 1-2 branches to some cacti
    if random.random() > 0.5:
        num_branches = random.randint(1, 2)
        for i in range(num_branches):
            branch_height = random.randint(10, 20)
            branch_width = random.randint(10, 15)
            branch_y = cactus['y'] + random.randint(10, cactus_height - 20)
            
            # Left or right branch
            if random.random() > 0.5:
                branch_x = cactus['x'] - branch_width
            else:
                branch_x = cactus['x'] + cactus_width
                
            cactus['branches'].append({
                'x': branch_x,
                'y': branch_y,
                'width': branch_width,
                'height': branch_height
            })
    
    return cactus

# Function to create a new power-up
def create_powerup():
    powerup_type = random.choice(['speed', 'points', 'shield'])
    powerup_size = 25
    
    # Create power-up at a random height
    powerup = {
        'x': SCREEN_WIDTH,
        'y': random.randint(GROUND_HEIGHT - 150, GROUND_HEIGHT - powerup_size),
        'width': powerup_size,
        'height': powerup_size,
        'type': powerup_type
    }
    
    return powerup

# Function to draw a cactus
def draw_cactus(cactus):
    # Main cactus body
    pygame.draw.rect(screen, CACTUS_COLOR, (
        cactus['x'], 
        cactus['y'], 
        cactus['width'], 
        cactus['height']
    ))
    
    # Draw branches if any
    for branch in cactus['branches']:
        pygame.draw.rect(screen, CACTUS_COLOR, (
            branch['x'],
            branch['y'],
            branch['width'],
            branch['height']
        ))

# Function to draw a power-up
def draw_powerup(powerup):
    # Choose color based on power-up type
    if powerup['type'] == 'speed':
        color = SPEED_COLOR
        symbol = "S"
    elif powerup['type'] == 'points':
        color = POINTS_COLOR
        symbol = "2x"
    else:  # shield
        color = SHIELD_COLOR
        symbol = "I"
    
    # Draw power-up circle
    pygame.draw.circle(screen, color, 
                      (powerup['x'] + powerup['width']//2, 
                       powerup['y'] + powerup['height']//2), 
                      powerup['width']//2)
    
    # Draw symbol
    symbol_text = small_font.render(symbol, True, WHITE)
    symbol_rect = symbol_text.get_rect(center=(powerup['x'] + powerup['width']//2, 
                                              powerup['y'] + powerup['height']//2))
    screen.blit(symbol_text, symbol_rect)

# Function to check collision between dinosaur and object
def check_collision(dino_x, dino_y, dino_width, dino_height, obj):
    # Simplified collision box for dinosaur (smaller than visual representation)
    dino_hitbox = {
        'x': dino_x + 10,
        'y': dino_y + 20,
        'width': dino_width - 20,
        'height': dino_height - 20
    }
    
    # Check collision with main object
    if (dino_hitbox['x'] < obj['x'] + obj['width'] and
        dino_hitbox['x'] + dino_hitbox['width'] > obj['x'] and
        dino_hitbox['y'] < obj['y'] + obj['height'] and
        dino_hitbox['y'] + dino_hitbox['height'] > obj['y']):
        return True
        
    # Check collision with branches if it's a cactus
    if 'branches' in obj:
        for branch in obj['branches']:
            if (dino_hitbox['x'] < branch['x'] + branch['width'] and
                dino_hitbox['x'] + dino_hitbox['width'] > branch['x'] and
                dino_hitbox['y'] < branch['y'] + branch['height'] and
                dino_hitbox['y'] + dino_hitbox['height'] > branch['y']):
                return True
    
    return False

# Function to draw clouds
def draw_clouds():
    for cloud in clouds:
        pygame.draw.ellipse(screen, WHITE, (cloud['x'], cloud['y'], cloud['width'], cloud['height']))
        pygame.draw.ellipse(screen, WHITE, (cloud['x'] + cloud['width']*0.2, cloud['y'] - cloud['height']*0.2, cloud['width']*0.6, cloud['height']*0.6))
        pygame.draw.ellipse(screen, WHITE, (cloud['x'] + cloud['width']*0.1, cloud['y'] + cloud['height']*0.3, cloud['width']*0.4, cloud['height']*0.4))

# Function to draw active power-ups
def draw_active_powerups():
    y_pos = 60
    
    if has_speed_boost:
        speed_text = small_font.render(f"Speed Boost: {speed_boost_timer//FPS}s", True, SPEED_COLOR)
        screen.blit(speed_text, (SCREEN_WIDTH - 200, y_pos))
        y_pos += 25
        
    if has_double_points:
        points_text = small_font.render(f"Double Points: {double_points_timer//FPS}s", True, POINTS_COLOR)
        screen.blit(points_text, (SCREEN_WIDTH - 200, y_pos))
        y_pos += 25
        
    if has_shield:
        shield_text = small_font.render(f"Shield: {shield_timer//FPS}s", True, SHIELD_COLOR)
        screen.blit(shield_text, (SCREEN_WIDTH - 200, y_pos))

# Game loop
running = True
obstacle_timer = 0
powerup_timer = 0
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    # Reset game
                    game_over = False
                    score = 0
                    obstacles = []
                    powerups = []
                    dino_y = GROUND_HEIGHT - dino_height
                    dino_vel_y = 0
                    is_jumping = False
                    GAME_SPEED = original_game_speed
                    has_speed_boost = False
                    has_double_points = False
                    has_shield = False
                elif not is_jumping:
                    is_jumping = True
                    dino_vel_y = JUMP_FORCE
    
    if not game_over:
        # Apply gravity and update position
        if is_jumping:
            dino_y += dino_vel_y
            dino_vel_y += GRAVITY
            
            # Check if landed
            if dino_y >= GROUND_HEIGHT - dino_height:
                dino_y = GROUND_HEIGHT - dino_height
                is_jumping = False
                dino_vel_y = 0
        
        # Update animation counter
        animation_count = (animation_count + 1) % 12  # Slow down animation by cycling through 12 frames
        
        # Update score
        if has_double_points:
            score += 2
        else:
            score += 1
        
        # Increase game speed gradually
        if score % 500 == 0 and not has_speed_boost:
            GAME_SPEED += 0.5
            original_game_speed = GAME_SPEED
        
        # Update power-up timers
        if has_speed_boost:
            speed_boost_timer -= 1
            if speed_boost_timer <= 0:
                has_speed_boost = False
                GAME_SPEED = original_game_speed
                
        if has_double_points:
            double_points_timer -= 1
            if double_points_timer <= 0:
                has_double_points = False
                
        if has_shield:
            shield_timer -= 1
            if shield_timer <= 0:
                has_shield = False
        
        # Update obstacle timer and create new obstacles
        obstacle_timer += 1
        if obstacle_timer > random.randint(50, 150):  # Random interval between obstacles
            obstacles.append(create_cactus())
            obstacle_timer = 0
        
        # Update power-up timer and create new power-ups (less frequently than obstacles)
        powerup_timer += 1
        if powerup_timer > random.randint(300, 600):  # Random interval between power-ups
            powerups.append(create_powerup())
            powerup_timer = 0
        
        # Update obstacles
        for obstacle in obstacles[:]:
            obstacle['x'] -= GAME_SPEED
            
            # Check if obstacle is off screen
            if obstacle['x'] < -100:
                obstacles.remove(obstacle)
            
            # Check collision
            if check_collision(dino_x, dino_y, dino_width, dino_height, obstacle):
                if has_shield:
                    # Remove the obstacle instead of ending game
                    obstacles.remove(obstacle)
                else:
                    game_over = True
        
        # Update power-ups
        for powerup in powerups[:]:
            powerup['x'] -= GAME_SPEED
            
            # Check if power-up is off screen
            if powerup['x'] < -50:
                powerups.remove(powerup)
            
            # Check collision with power-up
            if check_collision(dino_x, dino_y, dino_width, dino_height, powerup):
                # Apply power-up effect
                if powerup['type'] == 'speed':
                    has_speed_boost = True
                    speed_boost_timer = 10 * FPS  # 10 seconds
                    GAME_SPEED = original_game_speed * 1.5  # 50% speed boost
                elif powerup['type'] == 'points':
                    has_double_points = True
                    double_points_timer = 15 * FPS  # 15 seconds
                elif powerup['type'] == 'shield':
                    has_shield = True
                    shield_timer = 8 * FPS  # 8 seconds
                
                # Remove collected power-up
                powerups.remove(powerup)
        
        # Update clouds
        for cloud in clouds:
            cloud['x'] -= cloud['speed']
            if cloud['x'] < -cloud['width']:
                cloud['x'] = SCREEN_WIDTH
                cloud['y'] = random.randint(50, 150)
    
    # Clear the screen
    screen.fill(SKY_COLOR)
    
    # Draw clouds
    draw_clouds()
    
    # Draw the ground
    pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 2)
    
    # Draw the dinosaur with animation
    draw_dinosaur(dino_x, dino_y, animation_count // 6)  # Change animation every 6 frames
    
    # Draw obstacles
    for obstacle in obstacles:
        draw_cactus(obstacle)
    
    # Draw power-ups
    for powerup in powerups:
        draw_powerup(powerup)
    
    # Draw score
    score_text = font.render(f'Score: {score}', True, BLACK)
    screen.blit(score_text, (SCREEN_WIDTH - 200, 20))
    
    # Draw active power-ups
    draw_active_powerups()
    
    # Draw game over message
    if game_over:
        game_over_text = font.render('Game Over! Press SPACE to restart', True, BLACK)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
    
    # Update the display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(FPS)

# Quit the game
pygame.quit()
sys.exit()
