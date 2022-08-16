import pygame, sys, random

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()
screen = pygame.display.set_mode((432, 768)) # 2x of each dimension of background image
clock = pygame.time.Clock()

game_speed = 2

font = pygame.font.Font("flappy-bird.ttf", 40)
score = 0
score_surface = font.render("Score " + str(score), True, (255, 255, 255))
score_rectangle = score_surface.get_rect(center = (288, 100))

ready_surface = pygame.transform.scale2x(pygame.image.load("images/ready.png").convert_alpha())
ready_rectangle = ready_surface.get_rect(center=(216, 384))

game_over = False
game_over_surface = pygame.transform.scale2x(pygame.image.load("images/game-over.png").convert_alpha())
game_over_rectangle = game_over_surface.get_rect(center=(216, 384))

background_surface = pygame.transform.scale2x(pygame.image.load("images/background.png").convert_alpha())
background_rectangle = background_surface.get_rect(topleft = (0, 0))

floor = pygame.transform.scale2x(pygame.image.load("images/floor.png").convert_alpha())
floor_rectangle = floor.get_rect(topleft = (0, 600))

bird_up = pygame.transform.scale2x(pygame.image.load("images/bird-upflap.png").convert_alpha())
bird_mid = pygame.transform.scale2x(pygame.image.load("images/bird-midflap.png").convert_alpha())
bird_down = pygame.transform.scale2x(pygame.image.load("images/bird-downflap.png").convert_alpha())
bird_list = [bird_up, bird_mid, bird_down]
bird_index = 0
bird_rectangle = bird_list[0].get_rect(center = (100, 384))
gravitational_acceleration = 0.1
bird_velocity = 0 # velocity of bird in the y-direction, its x-velocity is constant

bird_flap = pygame.USEREVENT
pygame.time.set_timer(bird_flap, 200)

pipe = pygame.transform.scale2x(pygame.image.load("images/pipe.png").convert_alpha())
pipes_top_pos = [350, 400, 450]
pipe_list = []
# We keep an int array representing the pipes in order to calculate the increment in score
# every time the bird fly past a pipe
pipe_list_for_score = []

spawn_pipe = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_pipe, int(3000/game_speed))

wing_sound = pygame.mixer.Sound("sound/wing.wav")
hit_sound = pygame.mixer.Sound("sound/hit.wav")
score_sound = pygame.mixer.Sound("sound/score.wav")
already = [] # To make a sound and increase game speed every 100 points


def draw_screen():
    global score
    screen.blit(background_surface, background_rectangle)
    screen.blit(bird_list[bird_index], bird_rectangle)

    for i in range(len(pipe_list)):
        if i % 2 == 0:
            screen.blit(pipe, pipe_list[i])
        else:
            screen.blit(pygame.transform.flip(pipe, False, True), pipe_list[i])
    
    screen.blit(floor, floor_rectangle)
    score_surface = font.render("Score " + str(score), True, (255, 255, 255))
    screen.blit(score_surface, score_rectangle)
    pygame.display.update()
    clock.tick(120) 

def move_objects():
    # Move the pipes and remove pipes that has disappeared
    for i in range(len(pipe_list)):
        pipe_list[i].centerx -= game_speed
        if pipe_list[i].right < 0:
            pipe_list.pop(i)
            break
    # Move the floor
    floor_rectangle.left -= game_speed
    if floor_rectangle.left < -240: # 240 = 2 * (floor_x_dimension - background_x_dimension)
        floor_rectangle.left = 0

    # Move the bird
    global bird_velocity
    bird_velocity += gravitational_acceleration
    bird_rectangle.centery += bird_velocity

def check_collision():
    global game_over
    for pipe_rectangle in pipe_list:
        if bird_rectangle.colliderect(pipe_rectangle):
            hit_sound.play()
            game_over = True
    if bird_rectangle.top <= 0 or bird_rectangle.bottom >= floor_rectangle.top:
        hit_sound.play()
        game_over = True

def calculate_score():
    # We calculate the score by, for every pipe, check if its x-coordinate its within 10%
    # change from the bird's x-coordinate. Once the score for the pipe is calculated,
    # we remove the pipe so that we don't end up with a bunch of unused pipe
    global score, game_speed
    i = 0
    while i < len(pipe_list_for_score):
        pipe_list_for_score[i] -= game_speed
        if 0.9*bird_rectangle.centerx < pipe_list_for_score[i] < 1.1*bird_rectangle.centerx:
            score += 10
            pipe_list_for_score.pop(i)
        i += 1
    if score != 0 and score % 100 == 0 and score not in already:
        score_sound.play()
        game_speed += 1
        pygame.time.set_timer(spawn_pipe, int(3000/game_speed))
        already.append(score)

game_start = False
while True:
    if not game_start:
        screen.blit(background_surface, background_rectangle)
        screen.blit(ready_surface, ready_rectangle)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                game_start = True

        continue
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                wing_sound.play()
                bird_velocity = -4
            elif event.key == pygame.K_SPACE and game_over:
                game_over = False
                pipe_list.clear()
                pipe_list_for_score.clear()
                already.clear()
                bird_rectangle = bird_list[0].get_rect(center = (100, 384))
                bird_velocity = 0
                score = 0
                game_speed = 2
                pygame.time.set_timer(spawn_pipe, int(3000/game_speed))
                
            elif event.key == pygame.K_x and game_over:
                pygame.quit()
                sys.exit()
        if event.type == spawn_pipe and not game_over:
            pipe_top_pos = random.choice(pipes_top_pos)
            pipe_list.append(pipe.get_rect(midtop = (500, pipe_top_pos)))
            pipe_list.append(pipe.get_rect(midtop = (500, pipe_top_pos-750)))
            pipe_list_for_score.append(500)
        if event.type == bird_flap and not game_over:
            if bird_index < 2:
                bird_index += 1 
            else:
                bird_index = 0

    if not game_over:
        draw_screen()
        move_objects()
        check_collision()
        calculate_score()
    else:
        screen.blit(game_over_surface, game_over_rectangle)
        pygame.display.update()
