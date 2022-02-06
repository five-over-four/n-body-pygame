import pygame
from collections import deque

# under the hood
class Settings:
    def __init__(self):
        self.fps = 100
        self.resolution = (1280,720)
        self.center = self.resolution[0]/2, self.resolution[1]/2
        self.gravity_constant = 0.01 # just how much we do at once.
        self.shot_factor = 3 # larger number means more sensitive shooting.

class Body:
    def __init__(self, x, y, m=1, v_x=0, v_y=0):
        self.x = x
        self.y = y
        self.m = m
        self.v_x = v_x # velocity components.
        self.v_y = v_y
        self.trail = deque([]) # fast removal of first element.
        self.trail_length = 0 # bit more efficient than computing len.

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

# format: x-pos,y-pos,mass,x-velocity,y-velocity. one body per row. ex. 200,200,24.5,-4,2
def load_system():
    import os
    path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path)
    loaded_bodies = []
    if "save.data" in os.listdir(path):
        with open("save.data", "r") as f:
            data = f.readlines()
            for line in data:
                loaded_bodies.append(Body(*[float(x) for x in line.split(",")]))
    else:
        with open("save.data", "w") as f:
            pass
    return loaded_bodies

# puts the current positions, masses, and velocities into save.data.
def save_system(bodies):
    with open("save.data", "w") as f:
        for body in bodies:
            f.write(f"{body.x},{body.y},{body.m},{body.v_x},{body.v_y}\n")

def update_caption(paused, default_mass):
    if paused:
        pygame.display.set_caption(f"N-body simulation. Default mass: {int(default_mass)} (PAUSED)")
    else:
        pygame.display.set_caption(f"N-body simulation. Default mass: {int(default_mass)} (PLAYING)")

def remove_body(pos, bodies):
    for body in bodies:
        if ((pos[0] - body.x)**2 + (pos[1] - body.y)**2)**(1/2) <= 5:
            bodies.remove(body)
            break
    return bodies

def main(settings, screen):

    clock = pygame.time.Clock()
    bodies = []
    shot = None                 # position of the placed body.
    mouse_toggle = False
    center_COM_toggle = True    # system CENTER OF MASS is always kept centered.
    paused = False
    trail_density = 3           # lower is more dense, >=1.
    max_trail = 100              # per body
    default_mass = 32
    counter = 0                 # modular with trail_density.
    body_removal_timer = 200    # in frames.
    update_caption(paused, default_mass)

    while True:

        screen.fill((0,0,0))

        # draw and iterate the bodies.
        for body in bodies:
            if not paused:
                body.tick(bodies)
            pygame.draw.circle(screen, (255,255,255), (body.x, body.y), 5)

        # make trails and drop fading tail end.
        if counter % trail_density == 0 and not paused:
            for body in bodies:
                body.trail.append((body.x,body.y))
                body.trail_length += 1
                if body.trail_length > max_trail:
                    body.trail.popleft()
                    body.trail_length -= 1

        # draw the trails.
        for body in bodies:
            for i, pos in enumerate(body.trail):
                factor = i/max_trail
                pygame.draw.circle(screen, (255 * factor, 255 * factor, 255 * factor), pos, 1)

        # draw the line and prospective body.
        if mouse_toggle:
            pygame.draw.circle(screen, (255,0,0), shot, 5)
            pygame.draw.line(screen, (255,255,255), shot, pygame.mouse.get_pos())

        # CONTROL SEGMENT.
        for e in pygame.event.get():

            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1: # left click.
                    mouse_toggle = True
                    shot = pygame.mouse.get_pos()
                elif e.button == 3: # right click.
                    bodies = remove_body(pygame.mouse.get_pos(), bodies)
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1: # left click.
                    mouse_toggle = False
                    x, y = pygame.mouse.get_pos()
                    velocity = ((shot[0] - x) * settings.shot_factor, (shot[1] - y) * settings.shot_factor)
                    body = Body(*shot, m=default_mass)
                    body.v_x, body.v_y = velocity
                    bodies.append(body)

            elif e.type == pygame.KEYDOWN:

                if e.key == pygame.K_DELETE:
                    bodies.clear()
                elif e.key == pygame.K_SPACE:
                    paused ^= True
                elif e.key == pygame.K_f:
                    center_COM_toggle ^= True
                elif e.key == pygame.K_PLUS:
                    default_mass *= 2
                elif e.key == pygame.K_MINUS:
                    default_mass *= 1/2 if default_mass > 1 else 1
                elif e.key == pygame.K_l:
                    bodies = load_system()
                elif e.key == pygame.K_s:
                    save_system(bodies)
                if e.key == pygame.K_ESCAPE:
                    exit()
                update_caption(paused, default_mass)

            elif e.type == pygame.QUIT:
                exit()

            elif e.type == pygame.VIDEORESIZE:
                settings.resolution = screen.get_size()
                settings.center = settings.resolution[0]/2, settings.resolution[1]/2

        # automatically keep COM centered. (actually not COM, doesn't take mass into account).
        if center_COM_toggle and bodies:
            center_of_mass = (sum(body.x for body in bodies)/len(bodies), sum(body.y for body in bodies)/len(bodies))
            diff_x = settings.center[0] - center_of_mass[0]
            diff_y = settings.center[1] - center_of_mass[1]
            for body in bodies:
                body.x += diff_x
                body.y += diff_y
                new_trail = deque([])
                for pos in body.trail:
                    new_trail.append((pos[0] + diff_x, pos[1] + diff_y))
                body.trail = new_trail

        # removes off-screen bodies every 200 frames.
        if body_removal_timer == 200:
            body_removal_timer = 0
            for body in bodies: # remove off-screen bodies.
                if 0 > body.x or body.x > settings.resolution[0] or 0 > body.y or body.y > settings.resolution[1]:
                    bodies.remove(body)

        body_removal_timer += 1
        counter = (counter + 1) % trail_density
        pygame.display.flip()
        clock.tick(settings.fps)


if __name__ == "__main__":

    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode(settings.resolution, pygame.RESIZABLE)
    main(settings, screen)