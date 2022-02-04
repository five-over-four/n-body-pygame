import pygame
import math

# under the hood
class Settings:
    def __init__(self):
        self.fps = 100
        self.resolution = (1280,720)
        self.center = self.resolution[0]/2, self.resolution[1]/2
        self.gravity_constant = 0.5 # just how much we do at once.
        self.shot_factor = 0.3 # larger number = shorter line shoots faster

class Body:
    def __init__(self, x, y, m=1):
        self.x = x
        self.y = y
        self.m = m
        self.v_x = 0
        self.v_y = 0

    def acceleration(self, other):
        diff_vec = (self.x - other.x, self.y - other.y)
        norm = ((self.x-other.x)**2 + (self.y-other.y)**2)**(1/2)
        return (diff_vec[0]/norm**2, diff_vec[1]/norm**2)

    def tick(self, others):
        for body in others:
            if body == self:
                continue
            accel = self.acceleration(body)
            self.v_x += -body.m * accel[0]
            self.v_y += -body.m * accel[1]
        self.move()

    def move(self):
        self.x += self.v_x * settings.gravity_constant
        self.y += self.v_y * settings.gravity_constant

def main(settings, screen):

    clock = pygame.time.Clock()
    pygame.display.set_caption(f"N-body simulation. Default mass: 1")
    bodies = []
    shot = None # this holds a coordinate that is then moved to bodies after you're done adjusting its speed.
    mouse_toggle = False
    center_COM_toggle = True # if this is on, CENTER OF MASS is always kept centered.
    trails = []
    i = 0
    dot_count = 50 # per body
    default_mass = 1

    while True:

        screen.fill((0,0,0))

        # draw and iterate the bodies.
        for body in bodies:
            pygame.draw.circle(screen, (255,255,255), (body.x, body.y), 5)
            body.tick(bodies)

        # draw trails
        if i % 5 == 0:
            for body in bodies:
                trails.append((body.x,body.y))
            if len(trails) > len(bodies) * dot_count: # 50 dots per body
                trails = trails[len(bodies):]
        b = len(trails)
        for k, trail in enumerate(trails):
            pygame.draw.circle(screen, (255 * (k/b), 255 * (k/b), 255 * (k/b)), trail, 1)

        # draw the line and prospective body
        if mouse_toggle:
            pygame.draw.circle(screen, (255,0,0), shot, 5)
            pygame.draw.line(screen, (255,255,255), shot, pygame.mouse.get_pos())

        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                mouse_toggle = True
                shot = pygame.mouse.get_pos()
            if e.type == pygame.MOUSEBUTTONUP:
                mouse_toggle = False
                x, y = pygame.mouse.get_pos()
                velocity = ((shot[0] - x) * settings.shot_factor, (shot[1] - y) * settings.shot_factor)
                body = Body(*shot, m=default_mass)
                body.v_x, body.v_y = velocity
                bodies.append(body)
                trails.clear()

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    exit()
                elif e.key == pygame.K_DELETE:
                    bodies.clear()
                    trails.clear()
                elif e.key == pygame.K_SPACE:
                    center_COM_toggle ^= True
                elif e.key == pygame.K_PLUS:
                    default_mass *= 2
                    pygame.display.set_caption(f"N-body simulation. Default mass: {default_mass}")
                elif e.key == pygame.K_MINUS:
                    default_mass *= 1/2 if default_mass > 1 else 1
                    pygame.display.set_caption(f"N-body simulation. Default mass: {default_mass}")

            elif e.type == pygame.QUIT:
                exit()

            elif e.type == pygame.VIDEORESIZE:
                settings.resolution = screen.get_size()
        
        if i == 200:
            i = 0
            for body in bodies:
                if 0 > body.x or body.x > settings.resolution[0] or 0 > body.y or body.y > settings.resolution[1]:
                    bodies.remove(body)

        # automatically keep COM centered.
        if center_COM_toggle and bodies:
            center_of_mass = (sum(body.x for body in bodies)/len(bodies), sum(body.y for body in bodies)/len(bodies))
            diff_x = settings.center[0] - center_of_mass[0]
            diff_y = settings.center[1] - center_of_mass[1]
            for body in bodies:
                body.x += diff_x
                body.y += diff_y
            for j, trail in enumerate(trails):
                trails[j] = (trail[0] + diff_x, trail[1] + diff_y)

        i += 1
        pygame.display.flip()
        clock.tick(settings.fps)


if __name__ == "__main__":

    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode(settings.resolution, pygame.RESIZABLE)
    main(settings, screen)