import pygame
from collections import deque
import json, os

# colour standards. chosen in settings.json.
colours = { "black": (0,0,0), "white": (255,255,255), "red": (255,0,0), \
            "green": (0,255,0), "blue": (0,0,255), "purple": (170,0,255), \
            "yellow": (255,255,0), "dark red": (40,0,0), "dark green": (0,40,0), \
            "dark blue": (0,0,40), "grey": (130,130,130), "dark grey": (30,30,30)
          }

# global settings singleton.
class Settings:
    def __init__(self):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.directory = os.listdir(self.path)
        if "dev_settings.json" in self.directory:
            self.config_file = self.path + "/dev_settings.json"
        elif "settings.json" in self.directory:
            self.config_file = self.path + "/settings.json"
        else:
            self.config_file = None
        self.load()
        self.softening_constant = 15 # avoids singularities in our gravity modelling.
        self.center = self.resolution[0]/2, self.resolution[1]/2
        self.gravity_constant = 10 # strength of gravity
        self.shot_factor = 0.4 # for some reason, the strength of the shot depends on gravity.
    
    def load(self):
        if self.config_file:
            with open(self.config_file) as f:
                    data = f.read()
            s = json.loads(data)
            try:
                res_temp = s["resolution"].split(",")
                self.bg_colour = colours[s["bg_colour"]]
                self.body_colour = colours[s["body_colour"]]
                self.trail_colour = colours[s["trail_colour"]]
                self.resolution = (int(res_temp[0]), int(res_temp[1]))
                self.fps = int(s["sim_precision"])
                self.trail_density = int(s["trail_density"])
                self.trail_length = int(s["trail_length"])
                self.default_mass = int(s["default_mass"])
                self.realistic_gravity = bool(int(s["realistic_gravity"]))
            except Exception as e:
                print(f"settings.json contains erronerous data.\nloading defaults...{e}")
                self.load_defaults()
        else:
            self.load_defaults()

    def load_defaults(self):
        self.bg_colour = (0,0,0)
        self.body_colour = (255,255,255)
        self.trail_colour = (255,255,255)
        self.resolution = (1280,720)
        self.fps = 100
        self.trail_density = 3
        self.trail_length = 100
        self.default_mass = 32
        self.realistic_gravity = 0

class Body:
    def __init__(self, x, y, m=1, v_x=0, v_y=0):
        self.x = x
        self.y = y
        self.m = m
        self.v_x = v_x # velocity components.
        self.v_y = v_y
        self.a_x = 0 # acceleration components.
        self.a_y = 0
        self.trail = deque([]) # fast removal of first element.
        self.trail_length = 0 # bit more efficient than computing len.

    def move(self): # straight up (vt + 1/2at^2)G.
        self.x += (self.v_x / settings.fps + self.a_x/(2*settings.fps**2)) * settings.gravity_constant
        self.y += (self.v_y / settings.fps + self.a_y/(2*settings.fps**2)) * settings.gravity_constant

# O(n^2/2+n) = O(n^2) algorithm for moving bodies. atrocious. practically a bit faster than just n^2 double looping.
def tick(bodies):
    visited = {bodies[0]}
    accel = (0,0)
    for body_a in bodies:
        for body_b in bodies:
            if body_b in visited:
                continue
            diff_x, diff_y = body_a.x - body_b.x, body_a.y - body_b.y
            norm = diff_x**2 + diff_y**2
            kernel = softening_kernel(norm)**2
            if not settings.realistic_gravity:
                accel = (diff_x/(norm+kernel), diff_y/(norm+kernel))
            else:
                accel = (diff_x/(norm+kernel)**1.5, diff_y/(norm+kernel)**1.5)
            body_a.v_x += -body_b.m * accel[0]
            body_a.v_y += -body_b.m * accel[1]
            body_b.v_x += body_a.m * accel[0]
            body_b.v_y += body_a.m * accel[1]
            body_a.a_x, body_a.a_y = accel
            body_b.a_x, body_b.a_y = accel
        visited.add(body_a)
    for body in bodies:
        body.move()

# returns softening factor based on distance.
def softening_kernel(d): 
    if d <= settings.softening_constant:
        return (settings.softening_constant - d) * settings.softening_constant
    return 0

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

def update_caption(paused):
    if paused:
        pygame.display.set_caption(f"N-body simulation. Default mass: {settings.default_mass} (PAUSED)")
    else:
        pygame.display.set_caption(f"N-body simulation. Default mass: {settings.default_mass} (PLAYING)")

def remove_body(pos, bodies):
    for body in bodies:
        if ((pos[0] - body.x)**2 + (pos[1] - body.y)**2)**0.5 <= 5:
            bodies.remove(body)
            break
    return bodies

def main(settings, screen):

    clock = pygame.time.Clock()
    bodies = []
    shot = None                 # position of the placed body.
    mouse_toggle = False
    center_COM_toggle = True    # system mean position is always kept centered.
    paused = False
    counter = 0                 # modular with trail_density.
    body_removal_timer = 200    # in frames.
    update_caption(paused)

    while True:

        screen.fill(settings.bg_colour)

        # iterate body positions, velcities, accelerations, and draw.
        if bodies:
            if not paused:
                tick(bodies)
            for body in bodies: # for precision, we must move all bodies after the computations. +n to time complexity.
                pygame.draw.circle(screen, settings.body_colour, (body.x, body.y), 5)

        # make trails and drop fading tail end.
        if counter % settings.trail_density == 0 and not paused:
            for body in bodies:
                body.trail.append((body.x,body.y))
                body.trail_length += 1
                if body.trail_length > settings.trail_length:
                    body.trail.popleft()
                    body.trail_length -= 1

        # draw the trails.
        for body in bodies:
            for i, pos in enumerate(body.trail):
                factor = i/settings.trail_length
                colour = [trail * factor + bg * (1 - factor) for trail, bg in zip(settings.trail_colour, settings.bg_colour)]
                pygame.draw.circle(screen, colour, pos, 1)
                
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
                elif e.button == 4: # scroll up.
                    settings.default_mass *= 2
                elif e.button == 5: # scroll down.
                    settings.default_mass *= 1/2 if settings.default_mass > 1 else 1
                update_caption(paused)

            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1: # left click.
                    mouse_toggle = False
                    x, y = pygame.mouse.get_pos()
                    velocity = ((shot[0] - x) * settings.shot_factor, (shot[1] - y) * settings.shot_factor)
                    body = Body(*shot, m=settings.default_mass)
                    body.v_x, body.v_y = velocity
                    bodies.append(body)

            elif e.type == pygame.KEYDOWN:

                if e.key == pygame.K_DELETE:
                    bodies.clear()
                elif e.key == pygame.K_SPACE:
                    paused ^= True
                elif e.key == pygame.K_f:
                    center_COM_toggle ^= True
                    print(f"Camera following on.") if center_COM_toggle else print(f"Camera following off.")
                elif e.key == pygame.K_r:
                    settings.realistic_gravity ^= True
                    if settings.realistic_gravity:
                        settings.gravity_constant = 10
                        settings.shot_factor = 0.4
                        # this is done because gravity is now 10x stronger and velocities are added based on gravity.
                        for body in bodies:
                            body.v_x /= settings.gravity_constant
                            body.v_y /= settings.gravity_constant
                        print("Realistic gravity on. (1/r^2)")
                    else:
                        for body in bodies:
                            body.v_x *= settings.gravity_constant
                            body.v_y *= settings.gravity_constant
                        settings.gravity_constant = 1
                        settings.shot_factor = 5
                        print("Realistic gravity off. (1/r)")
                elif e.key == pygame.K_PLUS:
                    settings.default_mass *= 2
                elif e.key == pygame.K_MINUS:
                    settings.default_mass *= 1/2 if settings.default_mass > 1 else 1
                elif e.key == pygame.K_l:
                    bodies = load_system()
                    print("System loaded.")
                elif e.key == pygame.K_s:
                    save_system(bodies)
                    print("System saved.")
                if e.key == pygame.K_ESCAPE:
                    exit()
                update_caption(paused)

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
        counter = (counter + 1) % settings.trail_density
        pygame.display.flip()
        clock.tick(settings.fps)

if __name__ == "__main__":

    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode(settings.resolution, pygame.RESIZABLE)
    main(settings, screen)