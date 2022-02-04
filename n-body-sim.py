import pygame
import math

# under the hood
class Settings:
    def __init__(self):
        self.fps = 100
        self.resolution = (1280,720)
        self.center = self.resolution[0]/2, self.resolution[1]/2
        self.timestep = 0.1
        self.movement_factor = 20

class Body:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v_x = 0
        self.v_y = 0

    def acceleration(self, other):
        diff_vec = (self.x - other.x, self.y - other.y)
        norm = ((self.x-other.x)**2 + (self.y-other.y)**2)**(1/2)
        return (settings.timestep * diff_vec[0]/norm**2, settings.timestep * diff_vec[1]/norm**2)

    def tick(self, others):
        delta_v = [] # list of tuples of velocity changes
        for body in others:
            if body == self:
                continue
            accel = self.acceleration(body)
            delta_v.append(accel)
        self.v_x += sum(-v[0] for v in delta_v) # add all the velocity changes on n bodies.
        self.v_y += sum(-v[1] for v in delta_v)
        self.move()

    def move(self):
        self.x += self.v_x * settings.movement_factor
        self.y += self.v_y * settings.movement_factor

def main(settings, screen):

    clock = pygame.time.Clock()
    bodies = [] # [Body(**circ(0)), Body(**circ(1.2)), Body(**circ(4/3))]
    trails = []
    i = 0
    dot_count = 50 # per body

    while True:

        screen.fill((0,0,0))
        for body in bodies:
            pygame.draw.circle(screen, (255,255,255), (body.x, body.y), 5)
            #pygame.draw.circle(screen, (255,255,255), com , 3)

        for body in bodies:
            body.tick(bodies)

        # draw trails
        if i % 5 == 0:
            for body in bodies:
                trails.append((body.x,body.y))
            if len(trails) > len(bodies) * dot_count: # 50 dots per body
                trails = trails[len(bodies):]
        b = len(trails)
        for k, trail in enumerate(trails):
            pygame.draw.circle(screen, (255 * (k/b),255 * (k/b),255 * (k/b)), trail, 1)

        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                bodies.append(Body(*pygame.mouse.get_pos()))
                trails.clear()

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    exit()
                elif e.key == pygame.K_DELETE:
                    bodies.clear()
                    trails.clear()
                elif e.key == pygame.K_SPACE:
                    center_of_mass = (sum(body.x for body in bodies)/len(bodies), sum(body.y for body in bodies)/len(bodies))
                    diff_x = settings.center[0] - center_of_mass[0]
                    diff_y = settings.center[1] - center_of_mass[1]
                    for body in bodies:
                        body.x += diff_x
                        body.y += diff_y
                    for j, trail in enumerate(trails):
                        trails[j] = (trail[0] + diff_x, trail[1] + diff_y)

            elif e.type == pygame.QUIT:
                exit()

            elif e.type == pygame.VIDEORESIZE:
                settings.resolution = screen.get_size()
        
        if i == 100:
            i = 0
            for body in bodies:
                if 0 > body.x or body.x > settings.resolution[0] or 0 > body.y or body.y > settings.resolution[1]:
                    bodies.remove(body)
        
        i += 1
        pygame.display.flip()
        clock.tick(settings.fps)


if __name__ == "__main__":

    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode(settings.resolution, pygame.RESIZABLE)
    main(settings, screen)