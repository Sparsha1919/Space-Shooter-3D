from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800

BOUND_X = 40          
BOUND_Y_TOP = 40      
BOUND_Y_BOTTOM = -35  
CAM_PAN_MAX_X = 30
CAM_PAN_MAX_Y = 20

# --- Core entities ---
plane_pos = [0, 0, 0]
bullets = []          
enemies = []           
asteroids = []         
boss = None            
boss_bullets = []      
enemy_bullets = []     
stars = []
particles = []         

# --- Pickups ---
weapon_box = None      
shield_box = None
life_box = None
weapon_timer = 500
shield_box_timer = 700
life_box_timer = 1000

# --- Player state & Progression ---
score = 0
level = 1              
lives = 5
MAX_LIVES = 5
game_over = False
game_won = False
shield_timer = 0
weapon_power_timer = 0
damage_flash = 0

# --- Boss state ---
boss_mode = False
boss_defeated = False
BOSS_TRIGGER_SCORE = 300
BOSS_MAX_HP = 40
boss_fire_timer = 0
boss_enraged = False

# --- Modes & Camera ---
camera_mode = "third"
cam_offset_x = 0
cam_offset_y = 0
time_step = 0
quadric = None
cheat_mode = False

def init_game():
    global plane_pos, bullets, enemies, asteroids, boss, boss_bullets, enemy_bullets, stars, particles
    global weapon_box, shield_box, life_box
    global weapon_timer, shield_box_timer, life_box_timer
    global score, level, lives, game_over, game_won, shield_timer, weapon_power_timer
    global damage_flash, boss_mode, boss_defeated, boss_fire_timer, boss_enraged
    global camera_mode, cam_offset_x, cam_offset_y, time_step, quadric, cheat_mode

    if quadric is None:
        quadric = gluNewQuadric()

    plane_pos = [0, 0, 0]
    bullets, boss_bullets, enemy_bullets, particles, asteroids = [], [], [], [], []
    enemies = [make_enemy() for _ in range(4)]
    stars = [[random.randint(-160, 160), random.randint(-100, 100), random.randint(-350, 0)] for _ in range(220)]

    weapon_box, shield_box, life_box = None, None, None
    weapon_timer, shield_box_timer, life_box_timer = 500, 700, 1000

    score, level = 0, 1
    lives = 5
    game_over, game_won = False, False
    shield_timer, weapon_power_timer, damage_flash = 0, 0, 0
    boss_mode, boss_defeated, boss_fire_timer, boss_enraged = False, False, 0, False
    camera_mode = "third"
    cam_offset_x, cam_offset_y, time_step = 0, 0, 0
    cheat_mode = False

def make_enemy():
    x = random.uniform(-BOUND_X, BOUND_X)
    y = random.uniform(BOUND_Y_BOTTOM, BOUND_Y_TOP)
    speed = random.uniform(0.5, 1.2)
    fire_timer = random.randint(40, 120) 
    return [x, y, -260, speed, fire_timer]

def make_asteroid():
    x = random.uniform(-BOUND_X, BOUND_X)
    y = random.uniform(BOUND_Y_BOTTOM, BOUND_Y_TOP)
    speed = random.uniform(1.0, 2.0)
    size = random.uniform(2.5, 5.0)
    return [x, y, -350, speed, size]

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_plane():
    if camera_mode == "first": return
    glPushMatrix()
    glTranslatef(plane_pos[0], plane_pos[1], plane_pos[2])
    
    # Body (Main Fuselage)
    if weapon_power_timer > 0: glColor3f(1.0, 0.8, 0.0)
    else: glColor3f(0.85, 0.85, 0.9)
    glPushMatrix()
    glScalef(1.0, 0.6, 3.2)
    glutSolidCube(3)
    glPopMatrix()
    
    # Nose (Pointier Front)
    glPushMatrix()
    glTranslatef(0, 0, -4.6)
    glColor3f(0.3, 0.3, 0.35)
    gluCylinder(quadric, 1.3, 0.1, 2.2, 12, 12)
    glPopMatrix()
    
    # Cockpit (Cyan glass)
    glPushMatrix()
    glTranslatef(0, 1.2, -1.0)
    glScalef(1.0, 0.8, 2.0)
    glColor3f(0.0, 0.8, 1.0)
    gluSphere(quadric, 1.0, 12, 12)
    glPopMatrix()
    
    # Main Wings
    glColor3f(0.2, 0.4, 0.8)
    glPushMatrix()
    glTranslatef(0, 0, 1.0)
    glScalef(6.5, 0.15, 1.5)
    glutSolidCube(3)
    glPopMatrix()

    # Tail Wing (Vertical Stabilizer)
    glColor3f(0.2, 0.4, 0.8)
    glPushMatrix()
    glTranslatef(0, 1.5, 4.0)
    glScalef(0.2, 1.5, 1.5)
    glutSolidCube(3)
    glPopMatrix()

    # Twin Engines & Thrusters
    glColor3f(0.4, 0.4, 0.4)
    for eng_x in [-2.5, 2.5]:
        glPushMatrix()
        glTranslatef(eng_x, -0.3, 2.0)
        gluCylinder(quadric, 0.6, 0.6, 2.5, 10, 10)
        # Engine Fire glow
        glTranslatef(0, 0, 2.5)
        glColor3f(1.0, 0.5, 0.0)
        gluSphere(quadric, 0.5 + 0.1 * math.sin(time_step * 0.5), 10, 10)
        glColor3f(0.4, 0.4, 0.4) 
        glPopMatrix()

    # Shield (Solid Sphere around plane)
    if shield_timer > 0:
        glColor3f(0.2, 0.7, 1.0)
        glPushMatrix()
        glTranslatef(0, 0.5, 1)
        glScalef(1.3, 0.9, 1.7)
        gluSphere(quadric, 6.5, 10, 10)
        glPopMatrix()
        
    glPopMatrix()

def draw_enemy(e):
    x, y, z, speed, fire_timer = e
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.6, 0.15, 0.15)
    glutSolidCube(4.5)
    glColor3f(0.9, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0, 0, 2.4)
    gluSphere(quadric, 1.2, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_asteroid(ast):
    x, y, z, spd, size = ast
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(size, size, size)
    glColor3f(0.45, 0.4, 0.4) 
    gluSphere(quadric, 1.0, 10, 10) 
    glPopMatrix()

def draw_boss():
    if not boss: return
    bx, by, bz, hp, direction, phase = boss
    pulse = 1.0 + math.sin(time_step * 0.1) * 0.15
    if boss_enraged: glColor3f(0.95, 0.25, 0.05)
    else: glColor3f(0.9, 0.1, 0.7)
    
    glPushMatrix()
    glTranslatef(bx, by, bz)
    glRotatef(time_step * (3 if boss_enraged else 1), 0, 1, 0)
    gluSphere(quadric, 13 * pulse, 15, 15)
    
    # Boss Eye
    glPushMatrix()
    glTranslatef(0, 2, 12 * pulse)
    glColor3f(1.0, 1.0, 0.2)
    gluSphere(quadric, 3.5 * pulse, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_pickup_box(box, base_color):
    if not box: return
    x, y, z = box
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(time_step * 2, 1, 1, 0)
    glColor3f(base_color[0], base_color[1], base_color[2])
    glutSolidCube(3.2)
    glPopMatrix()

def trigger_explosion(x, y, z, count=10):
    for _ in range(count):
        particles.append([[x, y, z], [random.uniform(-1.0, 1.0), random.uniform(0.5, 2.0), random.uniform(-1.0, 1.0)], random.uniform(3.0, 6.0)])

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(55, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == "first":
        gluLookAt(plane_pos[0], plane_pos[1], plane_pos[2] - 2, 
                  plane_pos[0], plane_pos[1], plane_pos[2] - 100, 
                  0, 1, 0)
    else:
        gluLookAt(plane_pos[0] * 0.3 + cam_offset_x, 40 + cam_offset_y, plane_pos[2] + 55, 
                  plane_pos[0] * 0.3, plane_pos[1], plane_pos[2] - 60, 
                  0, 1, 0)

def draw_damage_flash():
    if damage_flash > 0:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glColor3f(0.5, 0.0, 0.0)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(WINDOW_WIDTH, 0, 0)
        glVertex3f(WINDOW_WIDTH, WINDOW_HEIGHT, 0)
        glVertex3f(0, WINDOW_HEIGHT, 0)
        glEnd()
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setupCamera()

    # Stars
    glPointSize(2)
    glBegin(GL_POINTS)
    glColor3f(1, 1, 1)
    for s in stars: 
        glVertex3f(s[0], s[1], s[2])
    glEnd()

    # Particles
    glBegin(GL_POINTS)
    for p in particles:
        glColor3f(1.0, 0.5, 0.0)
        glVertex3f(p[0][0], p[0][1], p[0][2])
    glEnd()

    if not game_over and not game_won:
        draw_plane()
        draw_pickup_box(weapon_box, [0.9, 0.7, 0.1])
        draw_pickup_box(shield_box, [0.1, 0.6, 0.9])
        draw_pickup_box(life_box, [1.0, 0.1, 0.4])

        # Bullets
        if weapon_power_timer > 0: glColor3f(1.0, 1.0, 0.0)
        else: glColor3f(0.3, 1.0, 1.0)
        for b in bullets:
            glPushMatrix()
            glTranslatef(b[0], b[1], b[2])
            gluSphere(quadric, 1.0, 8, 8)
            glPopMatrix()

        # Enemy Bullets
        glColor3f(1.0, 0.2, 0.2)
        for eb in enemy_bullets:
            glPushMatrix()
            glTranslatef(eb[0], eb[1], eb[2])
            gluSphere(quadric, 1.0, 8, 8)
            glPopMatrix()

        for ast in asteroids: draw_asteroid(ast)

        # Boss Bullets
        glColor3f(0.9, 1.0, 1.0)
        for bb in boss_bullets:
            glPushMatrix()
            glTranslatef(bb[0][0], bb[0][1], bb[0][2])
            gluSphere(quadric, 2, 8, 8)
            glPopMatrix()

        if boss_mode and boss: draw_boss()
        else:
            for e in enemies: draw_enemy(e)
            
    else:
        if game_won: draw_text(WINDOW_WIDTH // 2 - 110, WINDOW_HEIGHT // 2, "BOSS DEFEATED - YOU WIN!")
        else: draw_text(WINDOW_WIDTH // 2 - 110, WINDOW_HEIGHT // 2, "MISSION FAILED")
        draw_text(WINDOW_WIDTH // 2 - 95, WINDOW_HEIGHT // 2 - 30, "PRESS 'R' TO RESTART")

    # HUD 
    draw_text(20, WINDOW_HEIGHT - 30, f"SCORE: {score}  |  LEVEL: {level}")
    draw_text(20, WINDOW_HEIGHT - 55, f"LIVES: {lives} / {MAX_LIVES}")

    if boss_mode and boss and not game_won and not game_over:
        draw_text(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 30, f"BOSS HP: {boss[3]} / {BOSS_MAX_HP}")
    elif not boss_mode:
        draw_text(20, WINDOW_HEIGHT - 80, f"BOSS AT SCORE {BOSS_TRIGGER_SCORE}")

    y_off = 110
    if weapon_power_timer > 0: draw_text(20, WINDOW_HEIGHT - y_off, f"WEAPON OVERCHARGE: {weapon_power_timer}"); y_off+=25
    if shield_timer > 0: draw_text(20, WINDOW_HEIGHT - y_off, f"SHIELD ACTIVE: {shield_timer}"); y_off+=25
    if cheat_mode: draw_text(20, WINDOW_HEIGHT - y_off, "AUTOPILOT ENGAGED")

    draw_text(20, 20, "WASD: Move | SPACE/L-Click: Fire | R-Click/F1/F3: Cam | C: Cheat | R: Restart")

    draw_damage_flash()

    glutSwapBuffers()

def keyboardListener(key, x, y):
    global cam_offset_x, cam_offset_y, cheat_mode
    global bullets, weapon_power_timer, plane_pos
    
    k = key.lower()
    
    if k == b'z': cam_offset_x, cam_offset_y = 0, 0
    if k == b'r' and (game_over or game_won): init_game()
    if k == b'c': cheat_mode = not cheat_mode  

    if not game_over and not game_won:
        if k == b' ':
            dmg = 2 if weapon_power_timer > 0 else 1
            bullets.append([plane_pos[0], plane_pos[1], plane_pos[2] - 4.6, dmg])

        if not cheat_mode:
            move_speed = 4.0
            if k == b'w': plane_pos[1] += move_speed
            if k == b's': plane_pos[1] -= move_speed
            if k == b'a': plane_pos[0] -= move_speed
            if k == b'd': plane_pos[0] += move_speed
            
            plane_pos[0] = max(-BOUND_X, min(BOUND_X, plane_pos[0]))
            plane_pos[1] = max(BOUND_Y_BOTTOM, min(BOUND_Y_TOP, plane_pos[1]))

def specialKeyListener(key, x, y):
    global camera_mode, cam_offset_x, cam_offset_y
    if key == GLUT_KEY_F1: camera_mode = "first"
    elif key == GLUT_KEY_F3: camera_mode = "third"
    
    pan_speed = 3.0
    if camera_mode == "third":
        if key == GLUT_KEY_LEFT: cam_offset_x += pan_speed
        if key == GLUT_KEY_RIGHT: cam_offset_x -= pan_speed
        if key == GLUT_KEY_UP: cam_offset_y -= pan_speed
        if key == GLUT_KEY_DOWN: cam_offset_y += pan_speed
        
        cam_offset_x = max(-CAM_PAN_MAX_X, min(CAM_PAN_MAX_X, cam_offset_x))
        cam_offset_y = max(-CAM_PAN_MAX_Y, min(CAM_PAN_MAX_Y, cam_offset_y))

def mouseListener(button, state, x, y):
    global camera_mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == "third": camera_mode = "first"
        else: camera_mode = "third"
        
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_over and not game_won:
            dmg = 2 if weapon_power_timer > 0 else 1
            bullets.append([plane_pos[0], plane_pos[1], plane_pos[2] - 4.6, dmg])

def idle():
    global score, level, lives, game_over, game_won, time_step, damage_flash
    global shield_timer, weapon_power_timer
    global weapon_box, shield_box, life_box
    global weapon_timer, shield_box_timer, life_box_timer
    global boss, boss_mode, boss_defeated, boss_fire_timer, boss_enraged
    global boss_bullets, enemy_bullets, bullets, particles, asteroids, enemies
    global cheat_mode, plane_pos
    
    if game_over or game_won: 
        glutPostRedisplay()
        return
        
    time_step += 1
    level = 1 + (score // 50) 

    if shield_timer > 0: shield_timer -= 1
    if weapon_power_timer > 0: weapon_power_timer -= 1
    if damage_flash > 0: damage_flash -= 1

    # --- ADVANCED AUTOPILOT / CHEAT MODE ---
    if cheat_mode and not game_over and not game_won:
        dodging = False
        hazard = None
        min_dist = 999
        
        # Check for incoming hazards to dodge
        for bb in boss_bullets:
            d = math.sqrt((bb[0][0]-plane_pos[0])**2 + (bb[0][1]-plane_pos[1])**2 + (bb[0][2]-plane_pos[2])**2)
            if d < 30 and d < min_dist: min_dist = d; hazard = bb[0]
            
        for eb in enemy_bullets:
            d = math.sqrt((eb[0]-plane_pos[0])**2 + (eb[1]-plane_pos[1])**2 + (eb[2]-plane_pos[2])**2)
            if d < 30 and d < min_dist: min_dist = d; hazard = eb
            
        for ast in asteroids:
            d = math.sqrt((ast[0]-plane_pos[0])**2 + (ast[1]-plane_pos[1])**2 + (ast[2]-plane_pos[2])**2)
            if d < 35 and d < min_dist: min_dist = d; hazard = ast

        if hazard:
            # Active Dodging Logic
            dx, dy = plane_pos[0] - hazard[0], plane_pos[1] - hazard[1]
            mag = math.sqrt(dx*dx + dy*dy) or 1
            plane_pos[0] += (dx/mag) * 3.5
            plane_pos[1] += (dy/mag) * 3.5
            dodging = True

        if not dodging:
            # Attack and Tracking Logic
            target = None
            if boss_mode and boss: target = boss
            elif enemies: target = max(enemies, key=lambda e: e[2]) 

            if target:
                # Smooth Tracking for high accuracy
                plane_pos[0] += (target[0] - plane_pos[0]) * 0.15
                safe_y = target[1] - 5 if not boss_mode else target[1] - 10
                plane_pos[1] += (safe_y - plane_pos[1]) * 0.15

        plane_pos[0] = max(-BOUND_X, min(BOUND_X, plane_pos[0]))
        plane_pos[1] = max(BOUND_Y_BOTTOM, min(BOUND_Y_TOP, plane_pos[1]))

        # High Fire Rate in Cheat Mode
        if time_step % 4 == 0: 
            bullets.append([plane_pos[0], plane_pos[1], plane_pos[2] - 4.6, 2 if weapon_power_timer > 0 else 1])


    # Pickups
    if not boss_mode:
        if weapon_timer > 0: weapon_timer -= 1
        elif weapon_box is None: weapon_box = [random.uniform(-BOUND_X, BOUND_X), random.uniform(BOUND_Y_BOTTOM, BOUND_Y_TOP), -300]; weapon_timer = random.randint(500, 1000)
        
        if shield_box_timer > 0: shield_box_timer -= 1
        elif shield_box is None: shield_box = [random.uniform(-BOUND_X, BOUND_X), random.uniform(BOUND_Y_BOTTOM, BOUND_Y_TOP), -300]; shield_box_timer = random.randint(700, 1200)

        if life_box_timer > 0: life_box_timer -= 1
        elif life_box is None and lives < MAX_LIVES: life_box = [random.uniform(-BOUND_X, BOUND_X), random.uniform(BOUND_Y_BOTTOM, BOUND_Y_TOP), -300]; life_box_timer = random.randint(1000, 1500)
    else: 
        weapon_box, shield_box, life_box = None, None, None

    for box_name in ("weapon_box", "shield_box", "life_box"):
        box = globals()[box_name]
        if box:
            box[2] += 2.0
            if math.sqrt((box[0] - plane_pos[0])**2 + (box[1] - plane_pos[1])**2 + (box[2] - plane_pos[2])**2) < 10:
                if box_name == "weapon_box": weapon_power_timer = 400
                elif box_name == "shield_box": shield_timer = 400
                elif box_name == "life_box": lives = min(MAX_LIVES, lives + 1)
                trigger_explosion(plane_pos[0], plane_pos[1], plane_pos[2], 15)
                globals()[box_name] = None

    # Particles & Stars
    for p in particles[:]:
        p[0][0] += p[1][0]; p[0][1] += p[1][1]; p[0][2] += p[1][2]; p[2] -= 0.1
        if p[2] <= 0: particles.remove(p)
    for s in stars:
        s[2] += 5.0
        if s[2] > 60: 
            s[2] = -350
            s[0], s[1] = random.randint(-160, 160), random.randint(-100, 100)

    # Player Bullets
    for b in bullets[:]:
        b[2] -= 15.0
        if b[2] < -350: bullets.remove(b)

    # Boss Logic
    if score >= BOSS_TRIGGER_SCORE and not boss_mode and not boss_defeated:
        boss_mode = True
        boss = [0, 0, -220, BOSS_MAX_HP, 1.2, 0]
        boss_fire_timer = 0
        boss_bullets = []
        boss_enraged = False

    if boss_mode and boss:
        boss_speed = 1.5 if boss_enraged else 0.8
        boss[0] += boss_speed if boss[4] > 0 else -boss_speed
        if abs(boss[0]) > 60: boss[4] *= -1
        boss[2] += 0.1
        boss_enraged = boss[3] <= BOSS_MAX_HP * 0.5
        
        boss_fire_timer += 1
        if boss_fire_timer > (40 if boss_enraged else 70):
            boss_fire_timer = 0
            dist = math.sqrt((plane_pos[0]-boss[0])**2 + (plane_pos[1]-boss[1])**2 + (plane_pos[2]-boss[2])**2) or 1
            bx, by, bz = ((plane_pos[0]-boss[0])/dist)*2.0, ((plane_pos[1]-boss[1])/dist)*2.0, ((plane_pos[2]-boss[2])/dist)*2.0
            boss_bullets.append([[boss[0], boss[1], boss[2]], [bx, by, bz]])
            if boss_enraged:
                for ang in (-0.35, 0.35): 
                    boss_bullets.append([[boss[0], boss[1], boss[2]], [bx*math.cos(ang)-bz*math.sin(ang), by, bx*math.sin(ang)+bz*math.cos(ang)]])

        if math.sqrt((boss[0]-plane_pos[0])**2 + (boss[1]-plane_pos[1])**2 + (boss[2]-plane_pos[2])**2) < 15:
            if shield_timer <= 0: 
                lives -= 1
                damage_flash = 10
            trigger_explosion(plane_pos[0], plane_pos[1], plane_pos[2], 10)
            if lives <= 0: game_over = True

        for b in bullets[:]:
            if math.sqrt((boss[0]-b[0])**2 + (boss[1]-b[1])**2) < 22 and abs(boss[2]-b[2]) < 35:
                boss[3] -= b[3]
                trigger_explosion(b[0], b[1], b[2], 5)
                if b in bullets: bullets.remove(b)
                if boss[3] <= 0: 
                    trigger_explosion(boss[0], boss[1], boss[2], 40)
                    score += 200
                    boss_defeated = True
                    game_won = True

    # Enemy Logic
    elif not boss_mode:
        max_enemies = min(10, 4 + level)
        if len(enemies) < max_enemies: enemies.append(make_enemy())
        for e in enemies[:]:
            e_speed = e[3] * (1.0 + (level * 0.05)) 
            e[2] += e_speed
            
            e[4] -= 1
            if e[4] <= 0:
                enemy_bullets.append([e[0], e[1], e[2] + 5])
                e[4] = random.randint(50, max(60, 150 - (level * 5))) 

            if e[2] > 50: 
                e[:] = make_enemy()
                continue
            
            if math.sqrt((e[0]-plane_pos[0])**2 + (e[1]-plane_pos[1])**2 + (e[2]-plane_pos[2])**2) < 7:
                if shield_timer <= 0: 
                    lives -= 1
                    damage_flash = 10
                trigger_explosion(e[0], e[1], e[2], 10)
                e[:] = make_enemy()
                if lives <= 0: game_over = True
            
            for b in bullets[:]:
                if math.sqrt((e[0]-b[0])**2 + (e[1]-b[1])**2) < 8 and abs(e[2]-b[2]) < 25:
                    score += 10
                    trigger_explosion(e[0], e[1], e[2], 10)
                    if b in bullets: bullets.remove(b)
                    e[:] = make_enemy()
                    break

    # Asteroids Logic
    if not boss_mode:
        max_ast = min(6, 2 + (level // 2))
        if len(asteroids) < max_ast: asteroids.append(make_asteroid())
        for ast in asteroids[:]:
            ast[2] += ast[3] * (1.0 + (level * 0.05))
            if ast[2] > 50: 
                asteroids.remove(ast)
                continue
            
            if math.sqrt((ast[0]-plane_pos[0])**2 + (ast[1]-plane_pos[1])**2) < ast[4]*1.5 and abs(ast[2]-plane_pos[2]) < ast[4]*1.5 + 2:
                if shield_timer <= 0: 
                    lives -= 1
                    damage_flash = 10
                trigger_explosion(ast[0], ast[1], ast[2], 10)
                asteroids.remove(ast)
                if lives <= 0: game_over = True
                continue
            
            for b in bullets[:]:
                if math.sqrt((ast[0]-b[0])**2 + (ast[1]-b[1])**2) < ast[4]*1.5 and abs(ast[2]-b[2]) < ast[4]*1.5 + 5:
                    trigger_explosion(ast[0], ast[1], ast[2], 5)
                    if b in bullets: bullets.remove(b)
                    if ast in asteroids: asteroids.remove(ast)
                    score += 5
                    break

    # Enemy Bullets
    for eb in enemy_bullets[:]:
        eb[2] += (2.5 + (level * 0.1))
        if math.sqrt((eb[0]-plane_pos[0])**2 + (eb[1]-plane_pos[1])**2) < 4 and abs(eb[2]-plane_pos[2]) < 15:
            if shield_timer <= 0: 
                lives -= 1
                damage_flash = 10
            trigger_explosion(plane_pos[0], plane_pos[1], plane_pos[2], 5)
            if eb in enemy_bullets: enemy_bullets.remove(eb)
            if lives <= 0: game_over = True
            continue
        if eb[2] > 60: 
            if eb in enemy_bullets: enemy_bullets.remove(eb)

    # Boss Bullets
    for bb in boss_bullets[:]:
        bb[0][0] += bb[1][0]; bb[0][1] += bb[1][1]; bb[0][2] += bb[1][2]
        if math.sqrt((bb[0][0]-plane_pos[0])**2 + (bb[0][1]-plane_pos[1])**2 + (bb[0][2]-plane_pos[2])**2) < 5:
            if shield_timer <= 0: 
                lives -= 1
                damage_flash = 10
            trigger_explosion(plane_pos[0], plane_pos[1], plane_pos[2], 5)
            boss_bullets.remove(bb)
            if lives <= 0: game_over = True
            continue
        if bb[0][2] > 50: boss_bullets.remove(bb)

    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D OpenGL Plane Shooter")
    
    glEnable(GL_DEPTH_TEST)
    init_game()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()