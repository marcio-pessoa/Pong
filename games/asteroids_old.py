# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False

rock_group = set()
missile_group = set()
explosion_group = set()

messages_corage = ["May the Force be with you.", "Rocks are moving faster!", "Dead or alive you're coming with me", "Keep calm and carry a towel", "Is it better to be feared or respected? And I say: Is it too much to ask both?"]
messages_sorry = ["Try again!"]
messages_congratulations = ["Great!", "Good job."]

message_id = 0



class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated
    
    def get_center(self):
        return self.center
    
    def get_size(self):
        return self.size
    
    def get_radius(self):
        return self.radius
    
    def get_lifespan(self):
        return self.lifespan
    
    def get_animated(self):
        return self.animated
    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.s2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")


# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle - math.pi / 2
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .2
            self.vel[1] += acc[1] * .2
            
        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        self.thrust = on
        if on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += math.pi / 50
        
    def decrement_angle_vel(self):
        self.angle_vel -= math.pi / 50
        
    def shoot(self):
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        a_missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius

# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
    
    def draw(self, canvas):
        if self.animated:
            index = (self.age % self.lifespan) // 1
            center = [self.image_center[0] +  index * self.image_size[0], self.image_center[1]]
            canvas.draw_image(self.image, center, self.image_size, self.pos, self.image_size)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
    
    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        # update lifespan
        self.age += 1
        return self.age >= self.lifespan
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    def collide(self, other_object):
        if dist(self.pos, other_object.get_position()) < self.radius + other_object.get_radius():
            return True
        else:
            return False
    
    def spawn_distance(self, other_object):
        if dist(self.pos, other_object.get_position()) < self.radius + other_object.get_radius() * 2:
            return True
        else:
            return False

# key handlers to control ship   
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
        
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score, my_ship, time
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
        missile_group.intersection_update(set())
        started = True
        lives = 3
        score = 0
        timer.start()
        demo.stop()
        soundtrack.rewind()
        soundtrack.play()
        ship_thrust_sound.pause()
        ship_thrust_sound.set_volume(1)
        missile_sound.set_volume(.5)
        
def demonstration():
    action = random.choice([0, 1, 2, 3, 4])
    if action == 1:
        my_ship.decrement_angle_vel()
    elif action == 2:
        my_ship.increment_angle_vel()
    elif action == 3:
        my_ship.set_thrust(True)
    elif action == 4:
        my_ship.shoot()

def message(message, canvas):
    canvas.draw_text(str(message), [50, HEIGHT - 30], 22, "Silver", 'sans-serif')

def draw(canvas):
    global time, started, lives, score, message_id
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    
    # draw ship
    my_ship.draw(canvas)
    
    # update ship and sprites
    my_ship.update()
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    
    # check for collisions
    if group_collide(rock_group, my_ship):
        lives -= 1
        if lives < 1:
            started = False
            timer.stop()
            demo.start()
            rock_group.intersection_update(set())
            soundtrack.pause()
            ship_thrust_sound.set_volume(0)
            missile_sound.set_volume(0)

    # check for shot on the rock
    score += group_group_collide(missile_group, rock_group) * 10
    
    # boom rocks
    process_sprite_group(explosion_group, canvas)
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
    
    # draw UI
    canvas.draw_text("Lives", [50, 50], 22, "White", 'sans-serif')
    canvas.draw_text("Score", [680, 50], 22, "White", 'sans-serif')
    canvas.draw_text(str(lives), [50, 80], 22, "White", 'sans-serif')
    canvas.draw_text(str(score), [680, 80], 22, "White", 'sans-serif')
    
    if started == False:
        message("Demonstration mode", canvas)
    
    if time % 800 // 1 == 0:
        message_id = random.random() * len(messages) // 1

    if started == True and score % 100 // 1 == 0:
        message(messages[message_id], canvas)

# 
def group_collide(group, other_object):
    collision = False
    for i in set(group):
        if i.collide(other_object):
            group.remove(i)
            collision = True
            explosion = Sprite(i.get_position(), [0,0], 0, 0, explosion_image, explosion_info, explosion_sound)
            explosion_group.add(explosion)
    return collision

# 
def group_group_collide(group, other_group):
    collision = 0
    for i in set(group):
        l = group_collide(other_group, i)
        if l:
            group.remove(i)
        collision += l
    return collision

# 
def process_sprite_group(sprite_group, canvas):
    for i in set(sprite_group):
        i.draw(canvas)
        if(i.update()):
            sprite_group.remove(i)

# timer handler that spawns a rock    
def rock_spawner():
    while True:
        a_rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
        a_rock_vel = [random.random() * (.6 + score / 200) - .3, random.random() * (.6 + score / 200) - .3]
        a_rock_avel = random.random() * .2 - .1
        a_rock = Sprite(a_rock_pos, a_rock_vel, 0, a_rock_avel, asteroid_image, asteroid_info)
        
        # ship around bonus distance
        if a_rock.spawn_distance(my_ship):
            return
        
        if len (rock_group) < 12:
            rock_group.add(a_rock)
            break

# initialize stuff
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)

# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)
demo = simplegui.create_timer(250.0, demonstration)

# get things rolling
demo.start()
frame.start()