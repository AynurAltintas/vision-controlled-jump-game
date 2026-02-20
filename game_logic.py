import cv2
class Player:
    def __init__(self):
        self.x = 100
        self.y = 300
        self.width = 50
        self.height = 50

        self.velocity = 0
        self.gravity = 1
        self.jump_strength = -15

        self.on_ground = True

    def update(self, jump):
        if jump and self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False
        self.velocity += self.gravity
        self.y += self.velocity
        
        if self.y >= 300:
            self.y = 300
            self.on_ground = True
            self.velocity = 0
    def draw(self, frame):
        cv2.rectangle(
            frame,
            (self.x, int(self.y)), 
            (self.x + self.width, int(self.y) + self.height), 
            (255, 0, 0), 
            -1
        )
 