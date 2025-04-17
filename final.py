import random
import math

WIDTH = 1750 - 200
HEIGHT = 880 
TITLE = "Pink Galaxy Run"

menu_active = True
game_over = False
moving = False
on_ground = True
direction = "right"
invincible = False
invincibility_timer = 0
INVINCIBILITY_DURATION = 120
lives = 3
score = 0
MUSIC_VOLUME = 0.3

sound_on = True
music_on = True

velocity_y = 0
gravity = 0.5
jump_force = -19
speed_x = 5
scroll_speed = 6
min_distance = 200

character = Actor('idle')
character.x = 100
character.y = 300
character.scale = 0.5

idle_frames = ['idle', 'idle_left', 'idle_2', 'idle_rigth']
walk_right_frames = ['walk1', 'walk2']
walk_left_frames = ['walk3', 'walk4']
jump_right_frame = 'player_jump_right'
jump_left_frame = 'player_jump_left'

current_frame = 0
frame_timer = 0
frame_delay = 10
idle_frame_delay = 30

NUM_ENEMIES = 1
enemy_walk_frames = ['fly_1', 'fly_2']
snail_left_frames = ['snail_1', 'snail_2']
snail_right_frames = ['snail_3', 'snail_4']
enemy_animation_speed = 0.1
snail_animation_speed = 0.1

platforms = [
    Actor("platform", (100, 500)),
    Actor("platform", (400, 400)),
    Actor("platform", (600, 650)),
    Actor("platform", (800, 850)),
    Actor("platform", (1000, 1000)),
]

initial_platform = platforms[0]
initial_platform_moving = False
predefined_heights = [300, 400, 500, 600, 700, 800]

stars = []
last_star_time = 0
star_spawn_interval = 2 * 60 

heart_items = []
last_heart_time = 0
heart_spawn_interval = 5 * 60 

background_image = Actor("background")
menu_box = Actor("background_menu", center=(WIDTH // 2, HEIGHT // 2))
game_over_image = Actor('game_over', center=(WIDTH//2, HEIGHT//2))
score_display = Actor('score', (WIDTH - 250, 30))
heart = Actor('heart_3', (120, 50))

play_button = Actor("button_play", center=(WIDTH // 2 - 120, 350 + 180))
restart_button = Actor("button_restart", center=(WIDTH // 2 + 120, 350 + 180))
music_button = Actor("button_music_on", center=(WIDTH // 2 + 60, 310 + 170))
sound_button = Actor("button_sound_on", center=(WIDTH // 2 + 60, 265 + 170))
exit_button = Actor("button_exit", center=(WIDTH - 550, HEIGHT // 5 + 150))
back_to_menu_button = Actor("button_back_to_menu", center=(WIDTH - 80, 30))

background_music = "background_music"

character.x = platforms[0].x
character.y = platforms[0].y - character.height // 2

class HeartItem:
    def __init__(self, platform_index, relative_x):
        self.platform_index = platform_index
        self.relative_x = relative_x
        self.actor = Actor('heart')
        self.actor.scale = 0.3
        self.update_position()
        
    def draw(self):
        self.actor.draw()
        
    def update(self):
        self.update_position()
        if character.colliderect(self.actor):
            if sound_on:
                sounds.heart.play()
            global lives
            if lives < 3:
                lives += 1
                heart_items.remove(self)
                if lives == 1:
                    heart.image = 'heart_1'
                elif lives == 2:
                    heart.image = 'heart_2'
                elif lives == 3:
                    heart.image = 'heart_3'
    
    def update_position(self):
        platform = platforms[self.platform_index]
        self.actor.pos = (
            platform.x - platform.width//2 + self.relative_x,
            platform.y - 70
        )

class Star:
    def __init__(self, platform_index, relative_x):
        self.platform_index = platform_index
        self.relative_x = relative_x
        self.actor = Actor('star')
        self.actor.scale = 0.3
        self.update_position()
        
    def draw(self):
        self.actor.draw()
        
    def update(self):
        self.update_position()
        if character.colliderect(self.actor):
            global score
            score += 1
            stars.remove(self)
            if sound_on:
                sounds.star.play()
    
    def update_position(self):
        platform = platforms[self.platform_index]
        self.actor.pos = (
            platform.x - platform.width//2 + self.relative_x,
            platform.y - 70
        )

class Snail:
    def __init__(self, platform_index, scale=0.5):
        self.platform_index = platform_index
        self.platform = platforms[platform_index]
        self.scale = scale
        self.speed = 1.0
        self.direction = random.choice([-1, 1])
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = snail_animation_speed 
        platform = self.platform
        platform_left = platform.x - platform.width//2
        platform_right = platform.x + platform.width//2
        self.relative_x = random.uniform(20, platform.width - 20)
        self.x = platform_left + self.relative_x
        self.y = platform.y - 50 
        initial_frames = snail_right_frames if self.direction > 0 else snail_left_frames
        self.actor = Actor(initial_frames[0], (self.x, self.y))
        self.actor.scale = self.scale

    def update(self):
        self.platform = platforms[self.platform_index]
        self.relative_x += self.speed * self.direction
        platform_left = 20  
        platform_right = self.platform.width - 20 
        if self.relative_x <= platform_left:
            self.direction = 1
            self.relative_x = platform_left
        elif self.relative_x >= platform_right:
            self.direction = -1
            self.relative_x = platform_right
        self.x = (self.platform.x - self.platform.width//2) + self.relative_x
        self.y = self.platform.y - 50
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            current_frames = snail_right_frames if self.direction > 0 else snail_left_frames
            self.animation_frame = (self.animation_frame + 1) % len(current_frames)
        self.actor.pos = (self.x, self.y)
        current_frames = snail_right_frames if self.direction > 0 else snail_left_frames
        self.actor.image = current_frames[self.animation_frame]

    def draw(self):
        self.actor.draw()

snails = [
    Snail(1),
]

class Enemy:
    def __init__(self, x, y, scale=0.5):
        self.x = x
        self.y = y
        self.scale = scale
        self.velocity = random.randint(2, 5)
        self.speed = random.randint(2, 5)
        self.animation_frame = 0
        self.animation_timer = 0
        
    def update(self):
        self.x -= self.velocity
        if self.x < 0:
            self.x = WIDTH + random.randint(50, 300)
            self.y = random.choice(predefined_heights)
        self.animation_timer += enemy_animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(enemy_walk_frames)
        self.actor = Actor(enemy_walk_frames[self.animation_frame], (self.x, self.y))
        self.actor.scale = self.scale

    def draw(self):
        self.actor.draw()

enemies = [Enemy(WIDTH + random.randint(100, 500), 
                random.choice(predefined_heights)) for _ in range(NUM_ENEMIES)]

def draw():
    screen.clear()
    screen.fill((30, 30, 30))
    background_image.draw()
    if menu_active:
        menu_box.draw()
        music_button.draw()
        sound_button.draw()
        exit_button.draw()
        play_button.draw()
        restart_button.draw()
    else:
        back_to_menu_button.draw()
        if not game_over:
            heart.draw()
            score_display.draw()
            screen.draw.text(str(score), center=(WIDTH - 190, 30), fontsize=40, color="white")
            
            for platform in platforms:
                platform.draw()
            
            if invincible and invincibility_timer % 10 < 5:
                character.opacity = 0.5
            else:
                character.opacity = 1.0
            character.draw()
            
            for enemy in enemies:
                enemy.draw()
            for snail in snails:
                snail.draw()
            for heart_item in heart_items:
                heart_item.draw()
            for star in stars:
                star.draw()
        else:
            game_over_image.draw()
            screen.draw.text(f"Final Score: {score}", center=(WIDTH//2, HEIGHT//2 + 250), fontsize=60, color="#F19CB7")

def on_mouse_down(pos):
    global menu_active, sound_on, music_on, game_over
    
    if game_over:
        reset_game()
        return

    if menu_active:
        if play_button.collidepoint(pos):
            if sound_on:
                sounds.click.play()
            menu_active = False
        
        if restart_button.collidepoint(pos):
            if sound_on:
                sounds.click.play()
            reset_game()

        elif sound_button.collidepoint(pos):
            sound_on = not sound_on
            sound_button.image = "button_sound_on" if sound_on else "button_sound_off"
            if sound_on:
                sounds.click.play()

        elif music_button.collidepoint(pos):
            music_on = not music_on
            music_button.image = "button_music_on" if music_on else "button_music_off"
            if music_on:
                music.play(background_music)
            else:
                music.stop()
            if sound_on:
                sounds.click.play()

        elif exit_button.collidepoint(pos):
            if sound_on:
                sounds.click.play()
            menu_active = False
    else:
        if back_to_menu_button.collidepoint(pos):
            if sound_on:
                sounds.click.play()
            menu_active = True

def on_key_down(key):
    global menu_active, game_over, lives
    
    if key == keys.ESCAPE:
        if menu_active:
            exit()
        else:
            menu_active = True
            
    if game_over and key == keys.R:
        reset_game()

def start_music():
    if music_on:
        music.set_volume(MUSIC_VOLUME)
        music.play(background_music)

def on_music_end():
    if music_on:
        music.play(background_music)

def update():
    global velocity_y, on_ground, lives, current_frame, frame_timer, direction, moving, initial_platform_moving, last_heart_time, invincible, invincibility_timer, last_star_time, score, game_over

    if menu_active or game_over:
        return
    
    if invincible:
        invincibility_timer -= 1
        if invincibility_timer <= 0:
            invincible = False
    
    moving = False

    if keyboard.left or keyboard.a:
        character.x -= speed_x
        direction = "left"
        moving = True
    if keyboard.right or keyboard.d:
        character.x += speed_x
        direction = "right"
        moving = True

    if character.x < 0:
        character.x = 0
    if character.x > WIDTH:
        character.x = WIDTH

    if (keyboard.up or keyboard.w) and on_ground:
        velocity_y = jump_force
        on_ground = False
        if sound_on:
            sounds.jump.play()

    velocity_y += gravity
    character.y += velocity_y

    on_ground = False
    for platform in platforms:
        platform.height = platform.height // 2
        if (character.y + character.height // 2 >= platform.y - 10 and
            character.y + character.height // 2 <= platform.y + 30): 
            if (character.x + character.width // 2 > platform.x - platform.width // 2 and 
                character.x - character.width // 2 < platform.x + platform.width // 2):
                character.y = platform.y - character.height // 2  
                velocity_y = 0 
                on_ground = True  
                break

    if character.y > HEIGHT:
        lives = 0 
        game_over = True  
        if sound_on:
            sounds.death.play()  
        return

    frame_timer += 1
    if frame_timer >= (idle_frame_delay if not moving else frame_delay):
        frame_timer = 0
        current_frame = (current_frame + 1)
        if not on_ground:
            character.image = jump_right_frame if direction == "right" else jump_left_frame
        elif moving:
            if direction == "right":
                current_frame %= len(walk_right_frames)
                character.image = walk_right_frames[current_frame]
            else:
                current_frame %= len(walk_left_frames)
                character.image = walk_left_frames[current_frame]
        else:
            current_frame %= len(idle_frames)
            character.image = idle_frames[current_frame]

    for platform in platforms:
        if platform == initial_platform:
            if initial_platform_moving:
                platform.x -= scroll_speed
        else:
            platform.x -= scroll_speed

        if platform.x < -platform.width:
            new_x = WIDTH + random.randint(50, 300)
            while any(abs(new_x - p.x) < min_distance for p in platforms):
                new_x = WIDTH + random.randint(50, 300)
            platform.x = new_x
            platform.y = random.choice(predefined_heights)
    
    if on_ground:
        if (character.x + character.width // 2 < initial_platform.x - initial_platform.width // 2 or 
            character.x - character.width // 2 > initial_platform.x + initial_platform.width // 2):
            initial_platform_moving = True
    
    for heart_item in heart_items[:]:
        heart_item.update()
        if heart_item.actor.x < -50:
            heart_items.remove(heart_item)
    
    last_heart_time += 1
    if last_heart_time >= heart_spawn_interval and len(heart_items) < 3 and lives < 3: 
        last_heart_time = 0
        spawn_heart()

    for star in stars[:]:
        star.update()
        if star.actor.x < -50:
            stars.remove(star)
    
    last_star_time += 1
    if last_star_time >= star_spawn_interval and len(stars) < 5:
        last_star_time = 0
        spawn_star()

    for enemy in enemies:
        enemy.update()
    
    for snail in snails:
        snail.update()
    
    if check_collision_with_enemies() and not game_over:
        if lives <= 0:
            reset_game()

def spawn_heart():
    if lives >= 3: 
        return
        
    platforms_out_of_screen = [
        (i, platform) for i, platform in enumerate(platforms)
        if platform.x > WIDTH 
        and not any(snail.platform_index == i for snail in snails) 
    ]
    
    if platforms_out_of_screen:
        platform_index, platform = random.choice(platforms_out_of_screen)
        relative_x = random.randint(30, int(platform.width - 30))
        heart_items.append(HeartItem(platform_index, relative_x))

def spawn_star():
    platforms_out_of_screen = [
        (i, platform) for i, platform in enumerate(platforms)
        if platform.x > WIDTH 
        and not any(snail.platform_index == i for snail in snails)
        and not any(heart_item.platform_index == i for heart_item in heart_items)
    ]
    
    if platforms_out_of_screen:
        platform_index, platform = random.choice(platforms_out_of_screen)
        relative_x = random.randint(30, int(platform.width - 30))
        stars.append(Star(platform_index, relative_x))

def reset_game():
    global heart_items, last_heart_time, lives, game_over, initial_platform_moving
    global velocity_y, on_ground, direction, moving, current_frame, frame_timer
    global invincible, invincibility_timer, stars, last_star_time, score
    
    heart_items.clear()
    last_heart_time = 0
    stars.clear()
    last_star_time = 0
    score = 0

    for snail in snails:
        platform = platforms[snail.platform_index]
        snail.relative_x = random.uniform(20, platform.width - 20)
        snail.direction = random.choice([-1, 1])
        snail.x = (platform.x - platform.width//2) + snail.relative_x
        snail.y = platform.y - 50

    lives = 3
    game_over = False
    heart.image = 'heart_3'
    initial_platform.pos = (100, 500)
    character.x = initial_platform.x
    character.y = initial_platform.y - character.height // 2
    velocity_y = 0
    on_ground = True
    direction = "right"
    moving = False
    current_frame = 0
    frame_timer = 0
    initial_platform_moving = False
    invincible = False
    invincibility_timer = 0

    for i, platform in enumerate(platforms):
        if i != 0:
            platform.x = 400 + i * 200
            platform.y = 400 + i * 150

    for enemy in enemies:
        enemy.x = WIDTH + random.randint(100, 500)
        enemy.y = random.choice(predefined_heights)
        enemy.animation_frame = 0
        enemy.animation_timer = 0

def check_collision_with_enemies():
    global lives, game_over, heart, invincible, invincibility_timer
    
    if invincible: 
        return False
    
    for enemy in enemies:
        if character.colliderect(enemy.actor):
            handle_collision()
            return True
    
    for snail in snails:
        if character.colliderect(snail.actor):
            handle_collision()
            return True
            
    return False

def handle_collision():
    global lives, game_over, heart, invincible, invincibility_timer
    
    if invincible:
        return
    
    if sound_on:
        sounds.hit.play()
    
    lives -= 1
    invincible = True
    invincibility_timer = INVINCIBILITY_DURATION
    
    if lives == 2:
        heart.image = 'heart_2'
    elif lives == 1:
        heart.image = 'heart_1'
    elif lives <= 0:
        if sound_on:
            sounds.death.play()
        game_over = True

start_music()