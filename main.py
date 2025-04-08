import pygame
from constants import *
from player import Player
from coords import Coords

def main():
    print("Staring Space Trader")
    print(f"screen size is: {SCREEN_WIDTH} x {SCREEN_HEIGHT}")
    pygame.init()
    #pygame.font.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock_tick = pygame.time.Clock()
    dt = 0

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    
    Player.containers = (updatable, drawable)
    Coords.containers = (updatable, drawable)
    player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, PLAYER_RADIUS)
    coord_text = Coords("Player Location: ", player)

    print(len(drawable))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        
        screen.fill((40,25,34))
        updatable.update(dt)

        for item in drawable:
            item.draw(screen)

        pygame.display.flip()
        dt = clock_tick.tick(60) / 1000



if __name__ == "__main__":
    main()