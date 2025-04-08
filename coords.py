import pygame

class Coords(pygame.sprite.Sprite):
    def __init__(self, title, pos_object):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.my_font = pygame.font.SysFont("Arial", 16)
        self.title = title
        self.pos_object = pos_object
        print("Coordinate object init")
       
        
    def draw(self, screen):
        text = f"{self.title} - {self.pos_object.position.x:.2f} : {self.pos_object.position.y:.2f}"
        text_surface = self.my_font.render(text,  True, (220, 0, 0))
        screen.blit(text_surface, (10,10))
        
    def update(self, dt):
        pass