import random
import tkinter as tk


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
HUD_WIDTH = 220
PLAY_WIDTH = WINDOW_WIDTH - HUD_WIDTH
GROUND_Y = 565
FPS_DELAY = 16

GRAVITY = 0.85
MOVE_SPEED = 5.0
JUMP_SPEED = 14.5
BULLET_SPEED = 11.5
ENEMY_BULLET_SPEED = 7.2

STAGE_COUNT = 6
STAGE_WIDTH = 1400
WORLD_WIDTH = STAGE_COUNT * STAGE_WIDTH
GOAL_X = WORLD_WIDTH - 180
ITEM_TYPES = ("spread", "rapid", "heavy")


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


class RectEntity:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.w

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.h

    def intersects(self, other) -> bool:
        return not (
            self.right <= other.left
            or self.left >= other.right
            or self.bottom <= other.top
            or self.top >= other.bottom
        )


class Platform(RectEntity):
    def __init__(self, x, y, w, h=18, color="#36465f"):
        super().__init__(x, y, w, h)
        self.color = color


class Bullet(RectEntity):
    def __init__(self, x, y, vx, owner, color="#ffe38a", damage=1, kind="normal"):
        width = 12 if kind != "heavy" else 16
        height = 4 if kind != "heavy" else 6
        super().__init__(x, y, width, height)
        self.vx = vx
        self.owner = owner
        self.color = color
        self.damage = damage
        self.kind = kind

    def update(self):
        self.x += self.vx


class Enemy(RectEntity):
    def __init__(self, x, y, patrol_left, patrol_right, kind="soldier"):
        height = 42 if kind == "soldier" else 50
        width = 34 if kind == "soldier" else 46
        super().__init__(x, y, width, height)
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.kind = kind
        self.vx = 1.25
        self.vy = 0.0
        self.health = 2 if kind == "soldier" else 5
        self.on_ground = False
        self.cooldown = random.randint(70, 120)
        self.alive = True
        self.facing = -1


class Item(RectEntity):
    def __init__(self, x, y, item_type):
        super().__init__(x, y, 24, 24)
        self.item_type = item_type
        self.alive = True
        self.bob = random.random() * 6.28


class Player(RectEntity):
    def __init__(self):
        super().__init__(120, 430, 34, 52)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing = 1
        self.health = 5
        self.invincible = 0
        self.shoot_cooldown = 0
        self.weapon = "basic"
        self.weapon_timer = 0


class RunAndGunGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Iron Front")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="#09101d",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.keys_down = set()
        self.after_id = None
        self.game_over = False
        self.victory = False
        self.score = 0
        self.camera_x = 0.0

        self.player = Player()
        self.platforms = []
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.items = []
        self.stage_index = 0
        self.stage_label = "1-1"
        self.stage_goal_x = STAGE_WIDTH - 180
        self.spawn_timer = 0

        self.draw_static_ui()
        self.create_world()
        self.bind_keys()
        self.update_hud()
        self.loop()

    def draw_static_ui(self):
        c = self.canvas

        c.create_rectangle(0, 0, PLAY_WIDTH, WINDOW_HEIGHT, fill="#08111f", outline="#1f2c44")
        c.create_rectangle(PLAY_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#09101c", outline="#1f2c44")
        c.create_rectangle(PLAY_WIDTH - 8, 0, PLAY_WIDTH, WINDOW_HEIGHT, fill="#12213a", outline="")

        c.create_text(
            PLAY_WIDTH + HUD_WIDTH // 2,
            52,
            text="IRON\nFRONT",
            fill="#f4f7ff",
            font=("Segoe UI", 22, "bold"),
            justify="center",
        )

        self.score_text = c.create_text(
            PLAY_WIDTH + 18,
            150,
            anchor="w",
            text="Score: 0",
            fill="#ffe9a6",
            font=("Segoe UI", 13, "bold"),
        )
        self.health_text = c.create_text(
            PLAY_WIDTH + 18,
            182,
            anchor="w",
            text="Health: 5",
            fill="#ff9fbf",
            font=("Segoe UI", 13, "bold"),
        )
        self.distance_text = c.create_text(
            PLAY_WIDTH + 18,
            214,
            anchor="w",
            text="Distance: 0",
            fill="#9ed8ff",
            font=("Segoe UI", 12, "bold"),
        )
        self.stage_text = c.create_text(
            PLAY_WIDTH + 18,
            246,
            anchor="w",
            text="Stage: 1-1",
            fill="#b7f0c3",
            font=("Segoe UI", 12, "bold"),
        )
        self.weapon_text = c.create_text(
            PLAY_WIDTH + 18,
            278,
            anchor="w",
            text="Weapon: BASIC",
            fill="#ffcf8e",
            font=("Segoe UI", 12, "bold"),
        )

        c.create_rectangle(PLAY_WIDTH + 10, 300, WINDOW_WIDTH - 10, 410, fill="#0d1728", outline="#273956", width=1)
        c.create_text(PLAY_WIDTH + HUD_WIDTH // 2, 320, text="Controls", fill="#9db1d6", font=("Segoe UI", 13, "bold"))
        c.create_text(
            PLAY_WIDTH + 18,
            365,
            anchor="w",
            text=(
                "A / Left   Move\n"
                "D / Right  Move\n"
                "W / Up     Jump\n"
                "Z / Enter  Shoot\n"
                "R          Restart\n"
                "Esc        Quit"
            ),
            fill="#d9e4ff",
            font=("Segoe UI", 10),
            justify="left",
        )

        self.message_text = c.create_text(
            PLAY_WIDTH + HUD_WIDTH // 2,
            560,
            text="Reach the end",
            fill="#ffe19e",
            font=("Segoe UI", 11, "bold"),
            width=180,
            justify="center",
        )

    def bind_keys(self):
        for key in ("Left", "a", "A"):
            self.root.bind(f"<KeyPress-{key}>", lambda event, k="left": self.keys_down.add(k))
            self.root.bind(f"<KeyRelease-{key}>", lambda event, k="left": self.keys_down.discard(k))
        for key in ("Right", "d", "D"):
            self.root.bind(f"<KeyPress-{key}>", lambda event, k="right": self.keys_down.add(k))
            self.root.bind(f"<KeyRelease-{key}>", lambda event, k="right": self.keys_down.discard(k))
        for key in ("Up", "w", "W"):
            self.root.bind(f"<KeyPress-{key}>", lambda event, k="jump": self.keys_down.add(k))
            self.root.bind(f"<KeyRelease-{key}>", lambda event, k="jump": self.keys_down.discard(k))
        self.root.bind("<KeyPress-z>", lambda event: self.shoot())
        self.root.bind("<KeyPress-Z>", lambda event: self.shoot())
        self.root.bind("<KeyPress-Return>", lambda event: self.shoot())
        self.root.bind("<r>", lambda event: self.restart())
        self.root.bind("<R>", lambda event: self.restart())
        self.root.bind("<Escape>", lambda event: self.root.destroy())

    def create_world(self):
        self.platforms = [Platform(0, GROUND_Y, WORLD_WIDTH, 75, "#20304a")]
        self.enemies = []
        self.items = []
        self.stage_index = 0
        self.load_stage(0)
        self.bullets = []
        self.enemy_bullets = []
        self.spawn_timer = 140

    def stage_theme(self, index):
        themes = [
            {"platform": "#3b4d6c", "accent": "#6ea7ff", "enemy": "soldier", "density": 0.8},
            {"platform": "#44566f", "accent": "#87d5ff", "enemy": "soldier", "density": 1.0},
            {"platform": "#5a526e", "accent": "#ffcf6d", "enemy": "soldier", "density": 1.1},
            {"platform": "#4c6a54", "accent": "#94f0b6", "enemy": "soldier", "density": 1.2},
            {"platform": "#6a4b4b", "accent": "#ff9f9f", "enemy": "tank", "density": 1.25},
            {"platform": "#51496d", "accent": "#f8c7ff", "enemy": "tank", "density": 1.35},
        ]
        return themes[index % len(themes)]

    def load_stage(self, stage_index):
        self.stage_index = stage_index
        self.stage_label = f"1-{stage_index + 1}"
        self.stage_goal_x = min((stage_index + 1) * STAGE_WIDTH - 180, GOAL_X)
        theme = self.stage_theme(stage_index)

        base_x = stage_index * STAGE_WIDTH
        if stage_index == 0:
            self.platforms = [Platform(0, GROUND_Y, WORLD_WIDTH, 75, "#20304a")]

        layout = [
            (90, 475, 180),
            (330, 420, 165),
            (610, 470, 220),
            (900, 395, 170),
            (1120, 445, 180),
        ]

        for idx, (x, y, w) in enumerate(layout):
            offset_x = base_x + x
            offset_y = y - stage_index * 4 + (idx % 2) * 6
            self.platforms.append(Platform(offset_x, offset_y, w, 18, theme["platform"]))

        extra_count = 4 + stage_index * 2
        for idx in range(extra_count):
            platform_x = base_x + 120 + idx * 170
            platform_y = 355 + ((idx + stage_index) % 3) * 35
            platform_w = 90 + (idx % 3) * 40
            self.platforms.append(Platform(platform_x, platform_y, platform_w, 16, theme["platform"]))

        enemy_count = 4 + stage_index * 2
        for idx in range(enemy_count):
            x = base_x + 220 + idx * (STAGE_WIDTH - 320) / max(1, enemy_count - 1)
            x = int(x)
            y = 428 if idx % 2 == 0 else 348
            kind = theme["enemy"] if idx >= enemy_count - 2 else "soldier"
            if idx == enemy_count - 1 and stage_index >= 4:
                kind = "tank"
            patrol_left = max(base_x + 60, x - 90)
            patrol_right = min(base_x + STAGE_WIDTH - 70, x + 120)
            self.enemies.append(Enemy(x, y, patrol_left, patrol_right, kind=kind))

        item_positions = [
            (base_x + 260, 300),
            (base_x + 760, 260),
            (base_x + 1180, 320),
        ]
        for idx, (x, y) in enumerate(item_positions):
            item_type = ITEM_TYPES[(stage_index + idx) % len(ITEM_TYPES)]
            self.items.append(Item(x, y, item_type))

        self.spawn_timer = 100 + stage_index * 12

    def restart(self):
        self.game_over = False
        self.victory = False
        self.score = 0
        self.camera_x = 0.0
        self.player = Player()
        self.keys_down.clear()
        self.create_world()
        self.canvas.itemconfigure(self.message_text, text="Reach the end")
        self.redraw()

    def shoot(self):
        if self.game_over or self.victory:
            return
        if self.player.shoot_cooldown > 0:
            return

        bullet_x = self.player.right if self.player.facing > 0 else self.player.left - 12
        bullet_y = self.player.y + 22

        if self.player.weapon == "spread":
            self.bullets.append(Bullet(bullet_x, bullet_y, self.player.facing * BULLET_SPEED, "player", color="#ffe38a", kind="normal"))
            self.bullets.append(Bullet(bullet_x, bullet_y - 8, self.player.facing * (BULLET_SPEED * 0.92), "player", color="#8de9ff", kind="normal"))
            self.bullets.append(Bullet(bullet_x, bullet_y + 8, self.player.facing * (BULLET_SPEED * 0.92), "player", color="#ff9f8a", kind="normal"))
            self.player.shoot_cooldown = 14
        elif self.player.weapon == "rapid":
            self.bullets.append(Bullet(bullet_x, bullet_y, self.player.facing * (BULLET_SPEED * 1.1), "player", color="#c6ff9e", kind="normal"))
            self.player.shoot_cooldown = 5
        elif self.player.weapon == "heavy":
            self.bullets.append(Bullet(bullet_x, bullet_y - 1, self.player.facing * (BULLET_SPEED * 0.85), "player", color="#ffcf6d", damage=2, kind="heavy"))
            self.player.shoot_cooldown = 18
        else:
            self.bullets.append(Bullet(bullet_x, bullet_y, self.player.facing * BULLET_SPEED, "player"))
            self.player.shoot_cooldown = 10

    def nearby_platforms(self, rect):
        return [platform for platform in self.platforms if not (platform.right < rect.left - 40 or platform.left > rect.right + 40)]

    def move_entity(self, entity, dx, dy):
        entity.x += dx
        for platform in self.nearby_platforms(entity):
            if entity.intersects(platform):
                if dx > 0:
                    entity.x = platform.left - entity.w
                elif dx < 0:
                    entity.x = platform.right

        entity.y += dy
        entity.on_ground = False
        for platform in self.nearby_platforms(entity):
            if entity.intersects(platform):
                if dy > 0:
                    entity.y = platform.top - entity.h
                    entity.vy = 0
                    entity.on_ground = True
                elif dy < 0:
                    entity.y = platform.bottom
                    entity.vy = 0

    def update_player(self):
        if self.game_over or self.victory:
            return

        move_dir = 0
        if "left" in self.keys_down:
            move_dir -= 1
        if "right" in self.keys_down:
            move_dir += 1

        self.player.vx = move_dir * MOVE_SPEED
        if move_dir != 0:
            self.player.facing = move_dir

        if "jump" in self.keys_down and self.player.on_ground:
            self.player.vy = -JUMP_SPEED
            self.player.on_ground = False

        self.player.vy += GRAVITY
        self.player.vy = min(self.player.vy, 16)

        self.move_entity(self.player, self.player.vx, self.player.vy)
        self.player.x = clamp(self.player.x, 0, WORLD_WIDTH - self.player.w)

        if self.player.y > WINDOW_HEIGHT + 100:
            self.take_damage(1)
            self.player.x = max(120, self.camera_x + 100)
            self.player.y = 430
            self.player.vy = 0

        if self.player.invincible > 0:
            self.player.invincible -= 1

        if self.player.shoot_cooldown > 0:
            self.player.shoot_cooldown -= 1

        target_camera = self.player.x - 180
        self.camera_x = clamp(target_camera, 0, WORLD_WIDTH - PLAY_WIDTH)

        if self.player.x >= self.stage_goal_x:
            if self.stage_index < STAGE_COUNT - 1:
                self.advance_stage()
            else:
                self.victory = True
                self.canvas.itemconfigure(self.message_text, text="MISSION CLEAR - R to restart")

    def advance_stage(self):
        next_stage = self.stage_index + 1
        self.score += 500
        self.load_stage(next_stage)
        self.player.x = next_stage * STAGE_WIDTH + 120
        self.player.y = 430
        self.player.vx = 0
        self.player.vy = 0
        self.player.on_ground = False
        self.camera_x = clamp(self.player.x - 180, 0, WORLD_WIDTH - PLAY_WIDTH)
        self.canvas.itemconfigure(self.message_text, text=f"Stage {self.stage_label}")

    def update_enemies(self):
        if self.game_over or self.victory:
            return

        for enemy in self.enemies:
            if not enemy.alive:
                continue

            enemy.vy += GRAVITY
            enemy.vy = min(enemy.vy, 16)

            if enemy.kind == "tank":
                enemy.vx = 0.8 * enemy.facing
            else:
                if enemy.x <= enemy.patrol_left:
                    enemy.facing = 1
                elif enemy.x >= enemy.patrol_right:
                    enemy.facing = -1
                enemy.vx = 1.45 * enemy.facing

            self.move_entity(enemy, enemy.vx, enemy.vy)

            if not enemy.on_ground:
                enemy.facing = -enemy.facing

            enemy.cooldown -= 1
            distance = abs((self.player.x + self.player.w / 2) - (enemy.x + enemy.w / 2))
            if enemy.cooldown <= 0 and distance < 420 and random.random() < 0.45:
                direction = 1 if self.player.x > enemy.x else -1
                self.enemy_bullets.append(
                    Bullet(
                        enemy.x + enemy.w / 2,
                        enemy.y + 18,
                        direction * ENEMY_BULLET_SPEED,
                        "enemy",
                        color="#ff8c8c",
                    )
                )
                enemy.cooldown = random.randint(75, 140)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < self.camera_x - 60 or bullet.x > self.camera_x + PLAY_WIDTH + 60:
                self.bullets.remove(bullet)
                continue

            hit = False
            for enemy in self.enemies:
                if enemy.alive and bullet.intersects(enemy):
                    enemy.health -= bullet.damage
                    hit = True
                    self.score += 50
                    if enemy.health <= 0:
                        enemy.alive = False
                        self.score += 200 if enemy.kind == "tank" else 100
                        if random.random() < 0.45:
                            self.items.append(Item(enemy.x + 6, max(220, enemy.y - 18), random.choice(ITEM_TYPES)))
                    break

            if hit:
                self.bullets.remove(bullet)

        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.x < self.camera_x - 60 or bullet.x > self.camera_x + PLAY_WIDTH + 60:
                self.enemy_bullets.remove(bullet)
                continue

            if bullet.intersects(self.player):
                self.enemy_bullets.remove(bullet)
                self.take_damage(1)
                continue

            for platform in self.platforms:
                if bullet.intersects(platform):
                    self.enemy_bullets.remove(bullet)
                    break

        for item in self.items[:]:
            if not item.alive:
                continue
            item.bob += 0.11
            item.y += 0.15 * random.choice((0, 0, 1, -1))
            if item.intersects(self.player):
                self.apply_item(item.item_type)
                item.alive = False
                self.score += 80

        self.items = [item for item in self.items if item.alive]

    def apply_item(self, item_type):
        if item_type == "spread":
            self.player.weapon = "spread"
            self.player.weapon_timer = 900
            self.canvas.itemconfigure(self.message_text, text="Spread Shot!")
        elif item_type == "rapid":
            self.player.weapon = "rapid"
            self.player.weapon_timer = 720
            self.canvas.itemconfigure(self.message_text, text="Rapid Fire!")
        elif item_type == "heavy":
            self.player.weapon = "heavy"
            self.player.weapon_timer = 540
            self.canvas.itemconfigure(self.message_text, text="Heavy Gun!")

    def update_weapon_timer(self):
        if self.player.weapon == "basic":
            return
        if self.player.weapon_timer > 0:
            self.player.weapon_timer -= 1
        if self.player.weapon_timer <= 0:
            self.player.weapon = "basic"

    def draw_background(self):
        c = self.canvas
        c.create_rectangle(0, 0, PLAY_WIDTH, WINDOW_HEIGHT, fill="", outline="", tags="world")

        bands = ["#0a1323", "#0d172a", "#101d33", "#14223a"]
        for index, color in enumerate(bands):
            top = index * 92
            c.create_rectangle(0, top, PLAY_WIDTH, top + 92, fill=color, outline="", tags="world")

        horizon = 260
        c.create_rectangle(0, horizon, PLAY_WIDTH, WINDOW_HEIGHT, fill="#09101d", outline="", tags="world")

        for i in range(24):
            offset = (self.camera_x * 0.18 + i * 210) % (PLAY_WIDTH + 240) - 120
            height = 45 + (i % 4) * 18
            ridge = [(offset, horizon + 115), (offset + 80, horizon + 115 - height), (offset + 160, horizon + 115)]
            c.create_polygon(ridge, fill="#111b2d", outline="", tags="world")

        for i in range(30):
            tower_x = (i * 188 + int(self.camera_x * 0.35)) % (PLAY_WIDTH + 260) - 130
            tower_h = 42 + (i % 5) * 12
            c.create_rectangle(tower_x, 265 - tower_h, tower_x + 12, 265, fill="#18253a", outline="", tags="world")
            c.create_rectangle(tower_x + 3, 265 - tower_h + 8, tower_x + 9, 265, fill="#243553", outline="", tags="world")

        for i in range(40):
            star_x = (i * 173 + int(self.camera_x * 0.35)) % PLAY_WIDTH
            star_y = (i * 97) % 180 + 18
            size = 1 if i % 3 else 2
            color = ["#bcd6ff", "#f8f6dc", "#8fc7ff"][i % 3]
            c.create_oval(star_x, star_y, star_x + size, star_y + size, fill=color, outline="", tags="world")

        glow_x = PLAY_WIDTH * 0.55 + (self.camera_x * 0.02)
        c.create_oval(glow_x - 180, 110, glow_x + 180, 430, fill="#23466e", outline="", tags="world")
        c.create_oval(glow_x - 120, 150, glow_x + 120, 380, fill="#12233c", outline="", tags="world")

        c.create_rectangle(0, GROUND_Y + 2, PLAY_WIDTH, WINDOW_HEIGHT, fill="#070d17", outline="", tags="world")

    def draw_player_sprite(self, screen_x):
        c = self.canvas
        y = self.player.y
        facing = self.player.facing
        shadow_w = 34 if facing > 0 else 30
        c.create_oval(screen_x + 3, y + self.player.h + 3, screen_x + shadow_w, y + self.player.h + 11, fill="#050910", outline="", tags="world")

        # head and helmet
        c.create_oval(screen_x + 9, y + 1, screen_x + 25, y + 18, fill="#dfe6f1", outline="#101726", width=1, tags="world")
        c.create_oval(screen_x + 11, y + 3, screen_x + 23, y + 14, fill="#f7fbff", outline="", tags="world")
        c.create_rectangle(screen_x + 8, y + 7, screen_x + 26, y + 12, fill="#8f9cb1", outline="", tags="world")
        c.create_oval(screen_x + 13, y + 6, screen_x + 16, y + 9, fill="#131a28", outline="", tags="world")
        c.create_oval(screen_x + 19, y + 6, screen_x + 22, y + 9, fill="#131a28", outline="", tags="world")

        # torso and armor
        c.create_rectangle(screen_x + 6, y + 18, screen_x + 28, y + 43, fill="#5e6f88", outline="#101726", width=1, tags="world")
        c.create_rectangle(screen_x + 8, y + 20, screen_x + 26, y + 41, fill="#f1f5fb", outline="", tags="world")
        c.create_rectangle(screen_x + 10, y + 23, screen_x + 24, y + 31, fill="#547fff", outline="", tags="world")
        c.create_rectangle(screen_x + 11, y + 32, screen_x + 23, y + 39, fill="#c9d4e3", outline="", tags="world")

        # legs
        c.create_polygon(screen_x + 8, y + 41, screen_x + 15, y + 41, screen_x + 12, y + 52, screen_x + 5, y + 52, fill="#2a3347", outline="", tags="world")
        c.create_polygon(screen_x + 18, y + 41, screen_x + 25, y + 41, screen_x + 29, y + 52, screen_x + 22, y + 52, fill="#2f394f", outline="", tags="world")
        c.create_rectangle(screen_x + 4, y + 50, screen_x + 13, y + 54, fill="#0f1624", outline="", tags="world")
        c.create_rectangle(screen_x + 21, y + 50, screen_x + 31, y + 54, fill="#0f1624", outline="", tags="world")

        # arms
        c.create_line(screen_x + 8, y + 26, screen_x + 2, y + 34, fill="#101726", width=3, tags="world")
        c.create_line(screen_x + 24, y + 26, screen_x + 31, y + 32, fill="#101726", width=3, tags="world")
        c.create_line(screen_x + 9, y + 27, screen_x + 14, y + 31, fill="#cfd8e5", width=2, tags="world")
        c.create_line(screen_x + 23, y + 27, screen_x + 19, y + 33, fill="#cfd8e5", width=2, tags="world")

        # gun
        if facing > 0:
            muzzle_x = screen_x + 31
            c.create_rectangle(screen_x + 22, y + 23, screen_x + 43, y + 28, fill="#1e2635", outline="#0c111b", width=1, tags="world")
            c.create_rectangle(screen_x + 28, y + 20, screen_x + 33, y + 26, fill="#c2ccd8", outline="#0c111b", width=1, tags="world")
            c.create_rectangle(screen_x + 20, y + 25, screen_x + 26, y + 31, fill="#6b768c", outline="#0c111b", width=1, tags="world")
            c.create_rectangle(screen_x + 40, y + 24, screen_x + 47, y + 27, fill="#9aa8ba", outline="#0c111b", width=1, tags="world")
        else:
            muzzle_x = screen_x - 1
            c.create_rectangle(screen_x - 10, y + 23, screen_x + 11, y + 28, fill="#1e2635", outline="#0c111b", width=1, tags="world")
            c.create_rectangle(screen_x + 4, y + 20, screen_x + 9, y + 26, fill="#c2ccd8", outline="#0c111b", width=1, tags="world")
            c.create_rectangle(screen_x + 8, y + 25, screen_x + 14, y + 31, fill="#6b768c", outline="#0c111b", width=1, tags="world")
            c.create_rectangle(screen_x - 7, y + 24, screen_x - 13, y + 27, fill="#9aa8ba", outline="#0c111b", width=1, tags="world")

        c.create_oval(muzzle_x + 2, y + 23, muzzle_x + 6, y + 27, fill="#ffe8a6", outline="", tags="world")

    def draw_enemy_sprite(self, enemy, screen_x):
        c = self.canvas
        if enemy.kind == "tank":
            c.create_oval(screen_x - 2, enemy.y + enemy.h + 4, screen_x + enemy.w + 6, enemy.y + enemy.h + 12, fill="#050910", outline="", tags="world")
            c.create_rectangle(screen_x, enemy.y + 10, screen_x + enemy.w, enemy.y + enemy.h, fill="#5a3540", outline="#1c1420", width=1, tags="world")
            c.create_rectangle(screen_x + 5, enemy.y + 14, screen_x + enemy.w - 5, enemy.y + enemy.h - 6, fill="#8b4f57", outline="", tags="world")
            c.create_rectangle(screen_x - 8, enemy.y + 18, screen_x + enemy.w + 10, enemy.y + 32, fill="#3f2531", outline="#1c1420", width=1, tags="world")
            c.create_rectangle(screen_x + 3, enemy.y + 2, screen_x + enemy.w - 3, enemy.y + 14, fill="#d5c6d1", outline="#1c1420", width=1, tags="world")
            c.create_rectangle(screen_x + 10, enemy.y + 4, screen_x + enemy.w - 10, enemy.y + 11, fill="#f0f0f4", outline="", tags="world")
            c.create_oval(screen_x + 11, enemy.y + 6, screen_x + 15, enemy.y + 10, fill="#111726", outline="", tags="world")
            c.create_oval(screen_x + 24, enemy.y + 6, screen_x + 28, enemy.y + 10, fill="#111726", outline="", tags="world")
            c.create_rectangle(screen_x + 30, enemy.y + 22, screen_x + 52, enemy.y + 28, fill="#2a1a24", outline="", tags="world")
        else:
            c.create_oval(screen_x + 1, enemy.y + enemy.h + 2, screen_x + 33, enemy.y + enemy.h + 10, fill="#050910", outline="", tags="world")
            c.create_oval(screen_x + 8, enemy.y + 0, screen_x + 24, enemy.y + 16, fill="#d9dfeb", outline="#111726", width=1, tags="world")
            c.create_oval(screen_x + 10, enemy.y + 2, screen_x + 22, enemy.y + 13, fill="#f5f8ff", outline="", tags="world")
            c.create_rectangle(screen_x + 7, enemy.y + 7, screen_x + 25, enemy.y + 12, fill="#8a98ad", outline="", tags="world")
            c.create_rectangle(screen_x + 5, enemy.y + 15, screen_x + 27, enemy.y + 37, fill="#e35e5e", outline="#111726", width=1, tags="world")
            c.create_rectangle(screen_x + 7, enemy.y + 18, screen_x + 25, enemy.y + 34, fill="#ff8b8b", outline="", tags="world")
            c.create_rectangle(screen_x + 8, enemy.y + 21, screen_x + 24, enemy.y + 27, fill="#f3c3c3", outline="", tags="world")
            c.create_line(screen_x + 6, enemy.y + 25, screen_x - 2, enemy.y + 32, fill="#111726", width=3, tags="world")
            c.create_line(screen_x + 25, enemy.y + 25, screen_x + 32, enemy.y + 32, fill="#111726", width=3, tags="world")
            c.create_line(screen_x + 10, enemy.y + 35, screen_x + 5, enemy.y + 43, fill="#111726", width=2, tags="world")
            c.create_line(screen_x + 22, enemy.y + 35, screen_x + 27, enemy.y + 43, fill="#111726", width=2, tags="world")
            c.create_rectangle(screen_x + 9, enemy.y + 16, screen_x + 23, enemy.y + 19, fill="#38455c", outline="", tags="world")
            if enemy.facing > 0:
                c.create_rectangle(screen_x + 26, enemy.y + 20, screen_x + 43, enemy.y + 24, fill="#d7deea", outline="#111726", width=1, tags="world")
                c.create_rectangle(screen_x + 37, enemy.y + 18, screen_x + 46, enemy.y + 22, fill="#8b97a8", outline="#111726", width=1, tags="world")
            else:
                c.create_rectangle(screen_x - 9, enemy.y + 20, screen_x + 8, enemy.y + 24, fill="#d7deea", outline="#111726", width=1, tags="world")
                c.create_rectangle(screen_x - 14, enemy.y + 18, screen_x - 5, enemy.y + 22, fill="#8b97a8", outline="#111726", width=1, tags="world")

    def draw_item_sprite(self, item, screen_x):
        c = self.canvas
        bob_offset = int((item.bob * 3) % 4)
        fill = {"spread": "#8de9ff", "rapid": "#c6ff9e", "heavy": "#ffcf6d"}[item.item_type]
        accent = {"spread": "#ffffff", "rapid": "#ffffff", "heavy": "#fff5db"}[item.item_type]
        c.create_oval(screen_x - 1, item.y + bob_offset + 2, screen_x + item.w + 1, item.y + item.h + bob_offset + 8, fill="#050910", outline="", tags="world")
        c.create_oval(screen_x, item.y + bob_offset, screen_x + item.w, item.y + item.h + bob_offset, fill=fill, outline="#152033", width=2, tags="world")
        c.create_oval(screen_x + 7, item.y + bob_offset + 6, screen_x + 17, item.y + bob_offset + 16, fill=accent, outline="", tags="world")
        c.create_text(screen_x + 12, item.y + 12 + bob_offset, text="P", fill="#0c1220", font=("Segoe UI", 9, "bold"), tags="world")

    def draw_bullet_sprite(self, bullet, screen_x):
        c = self.canvas
        if bullet.kind == "heavy":
            c.create_rectangle(screen_x - 1, bullet.y + 1, screen_x + bullet.w + 1, bullet.y + bullet.h + 4, fill="#261d10", outline="", tags="world")
            c.create_rectangle(screen_x, bullet.y, screen_x + bullet.w, bullet.y + bullet.h + 3, fill=bullet.color, outline="#6d5322", width=1, tags="world")
        else:
            c.create_rectangle(screen_x - 1, bullet.y + 1, screen_x + bullet.w + 1, bullet.y + bullet.h + 3, fill="#0a1018", outline="", tags="world")
            c.create_rectangle(screen_x, bullet.y, screen_x + bullet.w, bullet.y + bullet.h, fill=bullet.color, outline="#0f1624", width=1, tags="world")

    def take_damage(self, amount):
        if self.player.invincible > 0 or self.game_over or self.victory:
            return

        self.player.health -= amount
        self.player.invincible = 45
        self.canvas.itemconfigure(self.message_text, text="Hit!")

        if self.player.health <= 0:
            self.game_over = True
            self.canvas.itemconfigure(self.message_text, text="GAME OVER - R to restart")

    def update_spawn(self):
        if self.game_over or self.victory:
            return

        self.spawn_timer -= 1
        if self.spawn_timer > 0:
            return

        self.spawn_timer = random.randint(90, 150)
        spawn_x = self.camera_x + PLAY_WIDTH + random.randint(80, 180)
        spawn_x = min(spawn_x, WORLD_WIDTH - 60)

        for enemy in self.enemies:
            if enemy.alive and abs(enemy.x - spawn_x) < 140:
                return

        patrol_left = max(0, spawn_x - random.randint(80, 120))
        patrol_right = min(WORLD_WIDTH - 50, spawn_x + random.randint(110, 200))
        spawn_y = 430
        self.enemies.append(Enemy(spawn_x, spawn_y, patrol_left, patrol_right))

    def update_hud(self):
        self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")
        self.canvas.itemconfigure(self.health_text, text=f"Health: {self.player.health}")
        self.canvas.itemconfigure(self.distance_text, text=f"Distance: {int(self.player.x)}")
        self.canvas.itemconfigure(self.stage_text, text=f"Stage: {self.stage_label}")
        self.canvas.itemconfigure(self.weapon_text, text=f"Weapon: {self.player.weapon.upper()}")

    def redraw(self):
        self.canvas.delete("world")

        sky_tint = int(40 + (self.camera_x / WORLD_WIDTH) * 30)
        self.canvas.configure(bg=f"#{8:02x}{14 + sky_tint // 6:02x}{29 + sky_tint // 4:02x}")

        self.draw_background()

        for platform in self.platforms:
            screen_x = platform.x - self.camera_x
            if screen_x > PLAY_WIDTH + 80 or screen_x + platform.w < -80:
                continue
            top_color = platform.color
            body_color = "#172131"
            self.canvas.create_rectangle(
                screen_x,
                platform.y,
                screen_x + platform.w,
                platform.y + platform.h,
                fill=body_color,
                outline="#111827",
                tags="world",
            )
            self.canvas.create_rectangle(
                screen_x,
                platform.y,
                screen_x + platform.w,
                platform.y + 5,
                fill=top_color,
                outline="",
                tags="world",
            )
            self.canvas.create_rectangle(
                screen_x + 3,
                platform.y + 4,
                screen_x + platform.w - 4,
                platform.y + platform.h - 3,
                outline="#51627d",
                width=1,
                tags="world",
            )
            self.canvas.create_rectangle(screen_x + 8, platform.y + 6, screen_x + platform.w - 8, platform.y + 9, fill="#f3f8ff", outline="", tags="world")

        goal_screen_x = self.stage_goal_x - self.camera_x
        self.canvas.create_rectangle(goal_screen_x - 6, 330, goal_screen_x + 38, GROUND_Y, fill="#1c1730", outline="#7b5e24", width=2, tags="world")
        self.canvas.create_rectangle(goal_screen_x + 8, 330, goal_screen_x + 24, GROUND_Y, fill="#8c6a2a", outline="", tags="world")
        self.canvas.create_polygon(goal_screen_x + 24, 344, goal_screen_x + 58, 355, goal_screen_x + 24, 366, fill="#f2cf7b", outline="#8c6a2a", tags="world")
        self.canvas.create_text(goal_screen_x + 16, 316, text=f"{self.stage_label}", fill="#ffe6a8", font=("Segoe UI", 12, "bold"), tags="world")

        for enemy in self.enemies:
            if not enemy.alive:
                continue
            screen_x = enemy.x - self.camera_x
            if screen_x < -80 or screen_x > PLAY_WIDTH + 80:
                continue
            self.draw_enemy_sprite(enemy, screen_x)

        for bullet in self.bullets + self.enemy_bullets:
            screen_x = bullet.x - self.camera_x
            if -40 <= screen_x <= PLAY_WIDTH + 40:
                self.draw_bullet_sprite(bullet, screen_x)

        for item in self.items:
            screen_x = item.x - self.camera_x
            if -50 <= screen_x <= PLAY_WIDTH + 50:
                self.draw_item_sprite(item, screen_x)

        player_screen_x = self.player.x - self.camera_x
        blink = self.player.invincible > 0 and (self.player.invincible // 5) % 2 == 0
        if not blink:
            self.draw_player_sprite(player_screen_x)

        if self.game_over:
            self.canvas.create_text(PLAY_WIDTH / 2, 180, text="GAME OVER", fill="#ff8c8c", font=("Segoe UI", 26, "bold"), tags="world")
        elif self.victory:
            self.canvas.create_text(PLAY_WIDTH / 2, 180, text="MISSION CLEAR", fill="#ffe0a1", font=("Segoe UI", 26, "bold"), tags="world")

        if self.player.weapon != "basic":
            self.canvas.create_text(PLAY_WIDTH / 2, 220, text=self.player.weapon.upper(), fill="#bde8ff", font=("Segoe UI", 10, "bold"), tags="world")

        self.update_hud()

    def loop(self):
        self.update_player()
        self.update_enemies()
        self.update_bullets()
        self.update_spawn()
        self.update_weapon_timer()
        self.redraw()
        self.after_id = self.root.after(FPS_DELAY, self.loop)


def main():
    root = tk.Tk()
    RunAndGunGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()