import pygame
from constants import * 
from circleshape import CircleShape

class Player(CircleShape):
    def __init__(self, x,y, radius):
        super().__init__(x, y, radius)
        self.rotation = 0
        self.shot_timer = 0
        self.last_key_pressed = None
        #self.key_delay_counter = 0
        #self.image = pygame.transform.scale(pygame.image.load("shipbird2.webp"), (75, 75))
    
    # in the player class
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw(self, screen):
        pygame.draw.polygon(screen, "white", self.triangle(), 2)
        #screen.blit(self.image, pygame.Rect(self.position.x -35, self.position.y-35, 10, 10))
        
        
    def rotate(self, dt):
        self.rotation += (PLAYER_TURN_SPEED * dt)
        #self.rotation += 45

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        future_pos = self.position + forward * PLAYER_SPEED * dt
        if (future_pos.x - PLAYER_RADIUS/2 < 0) or (future_pos.y - PLAYER_RADIUS/2  < 0) or (future_pos.x + PLAYER_RADIUS/2 > SCREEN_WIDTH) or (future_pos.y + PLAYER_RADIUS/2 > SCREEN_HEIGHT):
            pass
        else:
            self.position += forward * PLAYER_SPEED * dt
            #self.position += forward * 30

    def update(self, dt):
        self.shot_timer -= dt
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and (self.last_key_pressed != "a"):
            self.rotate(-dt)
            self.last_key_pressed = "a"
            #self.key_delay_counter = dt * 1000
        if keys[pygame.K_d] and (self.last_key_pressed != "d"):
            self.rotate(dt)
            self.last_key_pressed = "d"
            #self.key_delay_counter = dt * 1000
        if keys[pygame.K_w] and (self.last_key_pressed != "w"):
            self.move(dt)
            self.last_key_pressed = "w"
            #self.key_delay_counter = dt * 1000
        if keys[pygame.K_s] and (self.last_key_pressed != "s"):
            self.move(-dt)
            self.last_key_pressed = "s"
            #self.key_delay_counter = dt * 1000

        self.last_key_pressed = None
        # if self.key_delay_counter > 0 :
        #     self.key_delay_counter -= 1
        # else:
        #     self.last_key_pressed = None