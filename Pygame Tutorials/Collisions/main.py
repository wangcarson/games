import pygame, sys, time

WIDTH = 1280
HEIGHT = 660

class StaticObstacle(pygame.sprite.Sprite):
    def __init__(self, pos, size, groups):
        super().__init__(groups)
        self.image = pygame.Surface(size)
        self.image.fill('yellow')
        self.rect = self.image.get_rect(topleft = pos)
        self.old_rect = self.rect.copy()
 
class MovingVerticalObstacle(StaticObstacle):
    def __init__(self, pos, size, groups):
        super().__init__(pos, size, groups)
        self.image.fill('green')
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2((0,1))
        self.speed = 450
        self.old_rect = self.rect.copy()
 
    def update(self, dt):
        self.old_rect = self.rect.copy() # previous frame
        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.pos.y = self.rect.y
            self.direction.y *= -1
        if self.rect.bottom < 120:
            self.rect.bottom = 120
            self.pos.y = self.rect.y
            self.direction.y *= -1
 
        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y) # current frame (after movement)
 
class MovingHorizontalObstacle(StaticObstacle):
    def __init__(self, pos, size, groups):
        super().__init__(pos, size, groups)
        self.image.fill('purple')
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2((1,0))
        self.speed = 400
        self.old_rect = self.rect.copy()
 
    def update(self, dt):
        self.old_rect = self.rect.copy() # previous frame
        if self.rect.right > 1000:
            self.rect.right = 1000
            self.pos.x = self.rect.x
            self.direction.x *= -1
        if self.rect.left < 600:
            self.rect.left = 600
            self.pos.x = self.rect.x
            self.direction.x *= -1
 
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x) # current frame
 
class Player(pygame.sprite.Sprite):
    def __init__(self, groups, obstacles):
        super().__init__(groups)
        
        # image
        self.image = pygame.Surface((30,60))
        self.image.fill('blue')
        
        # position
        self.rect = self.image.get_rect(topleft = (640,360))
        self.old_rect = self.rect.copy()
        
        # movement
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2()
        self.speed = 300

        self.obstacles = obstacles
 
    def input(self):
        keys = pygame.key.get_pressed()
 
        # movement input
        if keys[pygame.K_UP]: 
            self.direction.y = -1
        elif keys[pygame.K_DOWN]: 
            self.direction.y = 1
        else: 
            self.direction.y = 0
 
        if keys[pygame.K_RIGHT]: 
            self.direction.x = 1
        elif keys[pygame.K_LEFT]: 
            self.direction.x = -1
        else: 
            self.direction.x = 0
    
    def collision(self, direction):
        collision_sprites = pygame.sprite.spritecollide(self, self.obstacles, False)
        if collision_sprites:
            if direction == 'horizontal':
                for sprite in collision_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                        self.pos.x = self.rect.x
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                        self.pos.x = self.rect.x
        
            if direction == 'vertical':
                for sprite in collision_sprites:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.pos.y = self.rect.y
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        self.pos.y = self.rect.y

    def update(self, dt):
        self.old_rect = self.rect.copy()
        self.input()
 
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize() # prevents diagonal speed-up
         
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        self.collision('vertical')
        
class Ball(pygame.sprite.Sprite):
    def __init__(self, groups, obstacles, player):
        super().__init__(groups)
        self.image = pygame.Surface((40,40))
        self.image.fill('red')
        self.rect = self.image.get_rect(center = (640,360))
 
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(1,1)
        self.speed = 400
        self.old_rect = self.rect.copy()

        self.obstacles = obstacles
        self.player = player
    
    def collision(self, direction):
        collision_sprites = pygame.sprite.spritecollide(self, self.obstacles, False)

        if self.rect.colliderect(self.player.rect):
            collision_sprites.append(self.player)

        if collision_sprites:
            if direction == 'horizontal':
                for sprite in collision_sprites:
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right
                        self.pos.x = self.rect.x
                        self.direction.x *= -1
        
            if direction == 'vertical':
                for sprite in collision_sprites:
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom
                        self.pos.y = self.rect.y
                        self.direction.y *= -1
    
    def wall_collision(self, direction):
        if direction == 'horizontal':
            if self.rect.left < 0:
                self.rect.left = 0
                self.pos.x = self.rect.x
                self.direction.x *= -1
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
                self.pos.x = self.rect.x
                self.direction.x *= -1
 
        if direction == 'vertical':
            if self.rect.top < 0:
                self.rect.top = 0
                self.pos.y = self.rect.y
                self.direction.y *= -1
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT
                self.pos.y = self.rect.y
                self.direction.y *= -1
    
    def update(self, dt):
        self.old_rect = self.rect.copy()
 
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize() # prevents diagonal speed-up

        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        self.collision('horizontal')
        self.wall_collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.rect.y = round(self.pos.y)
        self.collision('vertical')
        self.wall_collision('vertical')
 
# general setup
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
 
# group setup
all_sprites = pygame.sprite.Group()
collision_sprites = pygame.sprite.Group()
 
# sprite setup
player = Player(all_sprites, collision_sprites)
StaticObstacle((100,300), (100,50), [all_sprites,collision_sprites])
StaticObstacle((800,550), (100,200), [all_sprites,collision_sprites])
StaticObstacle((900,200), (200,10), [all_sprites,collision_sprites])
MovingVerticalObstacle((200,300), (200,60), [all_sprites,collision_sprites])
MovingHorizontalObstacle((850,350), (100,100), [all_sprites,collision_sprites])
Ball(all_sprites, collision_sprites, player)
 
# loop
last_time = time.time()
while True:
    
    # delta time
    dt = time.time() - last_time
    last_time = time.time()
    
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
 
    # drawing and updating the screen
    screen.fill('black')
    all_sprites.update(dt)
    all_sprites.draw(screen)
 
    # display output
    pygame.display.update()