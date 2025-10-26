import math
import random
from pygame import Rect
import pgzrun

WIDTH, HEIGHT = 800, 600
TITLE = "A noite dos vampiros"

WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
BLUE = (70, 130, 180)
YELLOW = (255, 210, 50)
RED = (200, 50, 50)
GREEN_TXT = (180, 255, 180)

GROUND_TOP = 360
SOUND_ON = True
GAME_STATE = "menu"
_COLLIDED = False
_MUSIC_STARTED = False
MUSIC_NAME = "bgm"

BUTTONS = [
    (WIDTH // 2 - 120, 260, 240, 60, "INÍCIO"),
    (WIDTH // 2 - 120, 340, 240, 60, "SONS ON/OFF"),
    (WIDTH // 2 - 120, 420, 240, 60, "SAIR"),
]

DOOR_RECT = Rect((WIDTH - 100, GROUND_TOP + 150), (35, 60))
DOOR_T = {"t": 0.0}
BG = {"t": 0.0, "stars": [], "bats": [], "graves": []}

def init_vampire_background():
    random.seed(42)
    BG["stars"].clear()
    for layer, count in [(0, 50), (1, 40), (2, 30)]:
        for _ in range(count):
            BG["stars"].append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT//2),
                "layer": layer,
                "tw": random.random() * 2 * math.pi
            })
    BG["bats"].clear()
    for _ in range(8):
        y = random.randint(60, 220)
        speed = random.uniform(40, 90)
        dirn = random.choice([-1, 1])
        x = random.randint(0, WIDTH)
        BG["bats"].append({
            "x": x, "y": y, "speed": speed, "dir": dirn, "phase": random.random()*6.28
        })
    BG["graves"].clear()
    for _ in range(12):
        x = random.randint(40, WIDTH-40)
        h = random.randint(18, 28)
        BG["graves"].append({"x": x, "h": h})

def update_vampire_background(dt):
    BG["t"] += dt
    for b in BG["bats"]:
        b["x"] += b["dir"] * b["speed"] * dt
        b["y"] += math.sin(BG["t"]*2 + b["phase"]) * 20 * dt
        if b["dir"] > 0 and b["x"] > WIDTH + 20: b["x"] = -20
        if b["dir"] < 0 and b["x"] < -20: b["x"] = WIDTH + 20

def draw_vampire_background():
    for i, col in enumerate([
        (28, 8, 36),
        (44, 12, 56),
        (58, 16, 74),
        (72, 20, 92),
        (88, 24, 110)
    ]):
        screen.draw.filled_rect(Rect((0, i*(HEIGHT//5)), (WIDTH, HEIGHT//5)), col)
    moon_x, moon_y = WIDTH - 140, 90
    screen.draw.filled_circle((moon_x, moon_y), 34, (220, 220, 220))
    for offx, offy, r in [(-10, -6, 6), (8, -2, 5), (-4, 8, 4)]:
        screen.draw.filled_circle((moon_x+offx, moon_y+offy), r, (200, 200, 200))
    for s in BG["stars"]:
        tw = 0.5 + 0.5*math.sin(BG["t"]*2 + s["tw"])
        size = 1 + (s["layer"] == 0) + (1 if tw > 0.8 else 0)
        screen.draw.filled_rect(Rect((int(s["x"]), int(s["y"])), (size, size)), (235, 235, 255))
    def hill(y_base, amp, col):
        for x in range(0, WIDTH, 4):
            y = y_base + amp * math.sin((x * 0.01) + (BG["t"] * 0.1))
            screen.draw.filled_rect(Rect((x, int(y)), (4, HEIGHT - int(y))), col)
    hill(420, 18, (18, 30, 28))
    hill(460, 14, (12, 22, 20))
    base_y = 360
    screen.draw.filled_rect(Rect((100, base_y - 50), (220, 50)), (10, 10, 18))
    screen.draw.filled_rect(Rect((120, base_y - 120), (60, 120)), (10, 10, 18))
    screen.draw.filled_rect(Rect((115, base_y - 120), (70, 16)), (30, 12, 22))
    screen.draw.filled_rect(Rect((190, base_y - 160), (60, 160)), (10, 10, 18))
    screen.draw.filled_rect(Rect((185, base_y - 160), (70, 18)), (30, 12, 22))
    screen.draw.filled_rect(Rect((260, base_y - 110), (50, 110)), (10, 10, 18))
    screen.draw.filled_rect(Rect((255, base_y - 110), (60, 16)), (30, 12, 22))
    for wx in [135, 155, 205, 225, 275]:
        screen.draw.filled_rect(Rect((wx, base_y - 80), (10, 18)), (240, 200, 60))
    ground_y = 520
    for g in BG["graves"]:
        x = g["x"]
        h = g["h"]
        screen.draw.filled_rect(Rect((x - 8, ground_y - h), (16, h)), (30, 30, 38))
        screen.draw.line((x, ground_y - h - 10), (x, ground_y - h - 2), (50, 50, 60))
        screen.draw.line((x - 4, ground_y - h - 6), (x + 4, ground_y - h - 6), (50, 50, 60))
    for b in BG["bats"]:
        x, y = int(b["x"]), int(b["y"])
        w = 14
        screen.draw.line((x - w//2, y), (x, y - 4), (20, 20, 24))
        screen.draw.line((x + w//2, y), (x, y - 4), (20, 20, 24))

def start_music():
    global _MUSIC_STARTED
    if SOUND_ON and GAME_STATE in ("menu", "playing"):
        try:
            music.set_volume(0.7)
            if not _MUSIC_STARTED:
                music.play(MUSIC_NAME)
                _MUSIC_STARTED = True
        except Exception as e:
            print("Aviso: música não tocou:", e)
            _MUSIC_STARTED = False
    else:
        music.stop()
        _MUSIC_STARTED = False

class Anim:
    def __init__(self, frames, fps=6):
        self.frames = frames
        self.fps = fps
        self.time = 0.0
        self.index = 0
    def update(self, dt):
        self.time += dt
        frame_time = 1.0 / self.fps
        while self.time >= frame_time:
            self.time -= frame_time
            self.index = (self.index + 1) % len(self.frames)
    def current(self):
        return self.frames[self.index]

class Character:
    def __init__(self, x, y, speed, idle_frames, walk_frames, sprite_half=21):
        self.pos = [x, y]
        self.target = [x, y]
        self.speed = speed
        self.state = "idle"
        self.idle = Anim(idle_frames, 4)
        self.walk = Anim(walk_frames, 8)
        self.radius = 18
        self.sprite_half = sprite_half
        self.is_moving = False
        self.step_timer = 0.0
        self.STEP_INTERVAL = 0.28
    def set_target(self, x, y, from_click=False):
        self.target = [x, max(GROUND_TOP, y)]
        if from_click:
            self.is_moving = True
    def update(self, dt):
        dx, dy = self.target[0] - self.pos[0], self.target[1] - self.pos[1]
        d = math.hypot(dx, dy)
        if d > 2:
            self.state = "walk"
            ux, uy = dx/d, dy/d
            self.pos[0] += ux * self.speed * dt
            self.pos[1] += uy * self.speed * dt
            self.walk.update(dt)
            if self.is_moving and SOUND_ON:
                self.step_timer += dt
                if self.step_timer >= self.STEP_INTERVAL:
                    self.step_timer = 0.0
                    try: sounds.step.play()
                    except: pass
        else:
            if self.is_moving:
                self.is_moving = False
            self.state = "idle"
            self.idle.update(dt)
        self.pos[0] = max(20, min(WIDTH - 20, self.pos[0]))
        self.pos[1] = max(GROUND_TOP, min(HEIGHT - 20, self.pos[1]))
    def draw(self):
        frame = self.walk.current() if self.state == "walk" else self.idle.current()
        screen.blit(frame, (self.pos[0]-self.sprite_half, self.pos[1]-self.sprite_half))

class Enemy(Character):
    def __init__(self, x, y, speed, idle_frames, walk_frames, area_rect):
        super().__init__(x, y, speed, idle_frames, walk_frames)
        self.area = area_rect
        self._pick_new_waypoint()
    def _pick_new_waypoint(self):
        x1, y1, x2, y2 = self.area
        self.target = [random.randint(x1 + 20, x2 - 20),
                       random.randint(y1 + 20, y2 - 20)]
    def update(self, dt):
        super().update(dt)
        if math.hypot(self.pos[0]-self.target[0], self.pos[1]-self.target[1]) < 6:
            self._pick_new_waypoint()
    def draw_area(self):
        x1, y1, x2, y2 = self.area
        screen.draw.rect(Rect((x1, y1), (x2 - x1, y2 - y1)), (90, 90, 90))

hero = Character(120, 500, 120, ["hero_idle1", "hero_idle2"], ["hero_walk1", "hero_walk2"])
enemies = [
    Enemy(520, 420, 85, ["enemy_idle1", "enemy_idle2"], ["enemy_walk1", "enemy_walk2"], area_rect=(420, 360, 700, 480)),
    Enemy(460, 520, 70, ["enemy_idle1", "enemy_idle2"], ["enemy_walk1", "enemy_walk2"], area_rect=(320, 480, 620, 560)),
]

def set_win():
    global GAME_STATE, _MUSIC_STARTED
    GAME_STATE = "win"
    music.stop()
    _MUSIC_STARTED = False
    if SOUND_ON:
        try: sounds.win.play()
        except: pass

def draw_door():
    screen.draw.filled_rect(DOOR_RECT, (30, 120, 60))
    screen.draw.filled_rect(Rect((DOOR_RECT.x - 6, DOOR_RECT.y - 12),
                                 (DOOR_RECT.w + 12, 12)), (35, 28, 40))
    knob_y = DOOR_RECT.y + DOOR_RECT.h//2
    screen.draw.filled_circle((DOOR_RECT.x + DOOR_RECT.w - 10, knob_y), 3, (240, 200, 80))
    DOOR_T["t"] += 0.06
    for side in [-1, 1]:
        tx = DOOR_RECT.x + (-8 if side < 0 else DOOR_RECT.w + 8)
        ty = DOOR_RECT.y + 26
        screen.draw.filled_rect(Rect((tx-2, ty), (4, 18)), (30, 25, 20))
        flick = 6 + int(2 * math.sin(DOOR_T["t"] + side))
        screen.draw.filled_circle((tx, ty), 6, (230, 120, 40))
        screen.draw.filled_circle((tx, ty - 3), flick//2, (255, 220, 90))

def hero_touches_door():
    hx, hy = hero.pos
    r = hero.radius
    hero_box = Rect((int(hx - r), int(hy - r)), (int(2*r), int(2*r)))
    return hero_box.colliderect(DOOR_RECT)

def handle_collision():
    global GAME_STATE, _COLLIDED, _MUSIC_STARTED
    if _COLLIDED or GAME_STATE != "playing": return
    _COLLIDED = True
    music.stop()
    _MUSIC_STARTED = False
    if SOUND_ON:
        try: sounds.hit.play()
        except: pass
    GAME_STATE = "gameover"

def reset_game():
    global GAME_STATE, _COLLIDED
    _COLLIDED = False
    hero.pos[:] = [120, 500]
    hero.set_target(120, 500)
    hero.is_moving = False
    hero.step_timer = 0.0
    for e in enemies: e._pick_new_waypoint()
    GAME_STATE = "playing"
    start_music()

def to_menu():
    global GAME_STATE, _COLLIDED
    _COLLIDED = False
    GAME_STATE = "menu"
    start_music()

def update(dt):
    update_vampire_background(dt)
    if GAME_STATE != "playing": return
    hero.update(dt)
    for e in enemies:
        e.update(dt)
        if math.hypot(hero.pos[0]-e.pos[0], hero.pos[1]-e.pos[1]) < (hero.radius + e.radius):
            handle_collision()
            return
    if hero_touches_door():
        set_win()
        return

def draw():
    if GAME_STATE == "menu":
        draw_vampire_background()
        draw_menu()
        return
    draw_vampire_background()
    draw_door()
    screen.draw.text("Clique para mover. Evite os inimigos. Alcance a porta!", (20, 20), fontsize=28, color=WHITE)
    for e in enemies:
        e.draw()
    hero.draw()
    if GAME_STATE == "gameover":
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=72, color=RED)
        screen.draw.text("Click para voltar ao MENU", center=(WIDTH//2, HEIGHT//2 + 60), fontsize=36, color=WHITE)
    if GAME_STATE == "win":
        screen.draw.text("VOCÊ VENCEU!", center=(WIDTH//2, HEIGHT//2), fontsize=72, color=GREEN_TXT)
        screen.draw.text("Clique para voltar ao MENU", center=(WIDTH//2, HEIGHT//2 + 60), fontsize=36, color=WHITE)

def draw_menu():
    screen.fill(BLUE)
    screen.draw.text("A NOITE DOS VAMPIROS", center=(WIDTH//2, 140), fontsize=56, color=WHITE)
    screen.draw.text("Objetivo: alcance a porta sem encostar nos vampiros.", center=(WIDTH//2, 200), fontsize=26, color=WHITE)
    for (x, y, w, h, text) in BUTTONS:
        screen.draw.filled_rect(Rect((x, y), (w, h)), GRAY)
        screen.draw.rect(Rect((x, y), (w, h)), WHITE)
        screen.draw.text(text, center=(x + w // 2, y + h // 2), fontsize=28, color=YELLOW)

def on_mouse_down(pos):
    global SOUND_ON
    if GAME_STATE == "menu":
        for (x, y, w, h, text) in BUTTONS:
            if Rect((x, y), (w, h)).collidepoint(pos):
                if text == "INÍCIO": reset_game()
                elif text == "SONS ON/OFF":
                    SOUND_ON = not SOUND_ON
                    start_music()
                elif text == "SAIR": quit()
    elif GAME_STATE == "playing":
        x, y = pos
        y = max(GROUND_TOP, y)
        hero.set_target(x, y, from_click=True)
    elif GAME_STATE in ("gameover", "win"):
        to_menu()

init_vampire_background()
start_music()
pgzrun.go()
