
import math
import random
import time
import tkinter as tk
from dataclasses import dataclass


WIDTH = 900
HEIGHT = 720
FIELD_RIGHT = 660
BALL_RADIUS = 10
GRAVITY = 520.0
FPS_DELAY_MS = 16


@dataclass
class Vec2:
    x: float
    y: float

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, value: float):
        return Vec2(self.x * value, self.y * value)

    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self):
        length = self.length()
        if length < 1e-9:
            return Vec2(0.0, -1.0)
        return Vec2(self.x / length, self.y / length)


@dataclass
class Segment:
    a: Vec2
    b: Vec2
    restitution: float = 0.86
    boost: float = 0.0


@dataclass
class Bumper:
    center: Vec2
    radius: float
    score: int
    flash_until: float = 0.0
    canvas_id: int | None = None


class Flipper:
    def __init__(
        self,
        pivot: Vec2,
        length: float,
        rest_angle_deg: float,
        active_angle_deg: float,
        side: str,
    ):
        self.pivot = pivot
        self.length = length
        self.rest_angle = math.radians(rest_angle_deg)
        self.active_angle = math.radians(active_angle_deg)
        self.angle = self.rest_angle
        self.angular_velocity = 0.0
        self.pressed = False
        self.side = side

    @property
    def tip(self) -> Vec2:
        return Vec2(
            self.pivot.x + math.cos(self.angle) * self.length,
            self.pivot.y + math.sin(self.angle) * self.length,
        )

    def update(self, dt: float):
        target = self.active_angle if self.pressed else self.rest_angle
        difference = target - self.angle

        max_speed = 13.0 if self.pressed else 8.5
        desired_speed = max(-max_speed, min(max_speed, difference * 25.0))

        previous_angle = self.angle
        self.angle += desired_speed * dt

        if (difference > 0 and self.angle > target) or (difference < 0 and self.angle < target):
            self.angle = target

        self.angular_velocity = (self.angle - previous_angle) / max(dt, 1e-6)


class RetroPinball:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Retro Space Pinball - POWER v3")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg="#06101f",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.keys_down: set[str] = set()
        self.last_time = time.perf_counter()

        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.game_over = False
        self.ball_ready = True
        self.launching = False
        self.launch_elapsed = 0.0
        self.launch_duration = 0.90

        # Space 키를 누르는 동안 발사 세기를 충전한다.
        self.charging = False
        self.charge_started = 0.0
        self.charge_time_max = 1.60
        self.launch_power = 0.0

        self.message = "SPACE를 누르고 있다가 놓으세요"
        self.message_until = 0.0

        self.ball_pos = Vec2(610.0, 625.0)
        self.ball_vel = Vec2(0.0, 0.0)

        self.left_flipper = Flipper(Vec2(255, 610), 108, 18, -28, "left")
        self.right_flipper = Flipper(Vec2(425, 610), 108, 162, 208, "right")

        self.walls: list[Segment] = []
        self.targets: list[Bumper] = []
        self.bumpers: list[Bumper] = []

        self.ball_item = None
        self.left_flipper_item = None
        self.right_flipper_item = None
        self.score_item = None
        self.lives_item = None
        self.status_item = None
        self.power_bar_item = None
        self.power_text_item = None

        self.build_table()
        self.bind_keys()
        self.draw_dynamic()
        self.loop()

    def build_table(self):
        c = self.canvas

        # 배경 별
        random.seed(7)
        for _ in range(90):
            x = random.randint(20, FIELD_RIGHT - 20)
            y = random.randint(20, HEIGHT - 20)
            size = random.choice((1, 1, 1, 2))
            shade = random.choice(("#34506f", "#496783", "#6f8da8", "#9bb4c7"))
            c.create_oval(x, y, x + size, y + size, fill=shade, outline="")

        # 우측 정보 패널
        c.create_rectangle(FIELD_RIGHT, 0, WIDTH, HEIGHT, fill="#0d1830", outline="#20365c", width=3)
        c.create_text(
            780,
            55,
            text="RETRO\nSPACE PINBALL",
            fill="#8ef3ff",
            font=("Consolas", 23, "bold"),
            justify="center",
        )
        c.create_text(780, 145, text="SCORE", fill="#8aa7c8", font=("Consolas", 15, "bold"))
        self.score_item = c.create_text(
            780, 183, text="000000", fill="#fff39b", font=("Consolas", 28, "bold")
        )
        c.create_text(780, 240, text="BALLS", fill="#8aa7c8", font=("Consolas", 15, "bold"))
        self.lives_item = c.create_text(
            780, 277, text="● ● ●", fill="#ff8bbb", font=("Consolas", 21, "bold")
        )

        # 발사 세기 게이지
        c.create_text(
            780, 315, text="LAUNCH POWER",
            fill="#8aa7c8", font=("Consolas", 12, "bold")
        )
        c.create_rectangle(
            700, 336, 860, 356,
            fill="#07101f", outline="#6d89ac", width=2
        )
        self.power_bar_item = c.create_rectangle(
            703, 339, 703, 353,
            fill="#fff39b", outline=""
        )
        self.power_text_item = c.create_text(
            780, 375, text="0%",
            fill="#ffffff", font=("Consolas", 11, "bold")
        )

        c.create_text(
            780,
            445,
            text=(
                "조작법\n\n"
                "A / ←   왼쪽 플리퍼\n"
                "D / →   오른쪽 플리퍼\n"
                "SPACE   누르고 충전\n"
                "놓기    세기에 맞춰 발사\n"
                "R       다시 시작\n"
                "ESC     종료"
            ),
            fill="#d6e7ff",
            font=("맑은 고딕", 12),
            justify="left",
        )

        c.create_text(
            780,
            610,
            text="범퍼 +100\n타깃 +250\nSpace를 길게 눌러 강하게!",
            fill="#92a9ca",
            font=("맑은 고딕", 11),
            justify="center",
        )

        self.status_item = c.create_text(
            780,
            665,
            text=self.message,
            width=205,
            fill="#ffffff",
            font=("맑은 고딕", 12, "bold"),
            justify="center",
        )

        # 테이블 외곽
        c.create_polygon(
            36, 690,
            36, 110,
            90, 45,
            570, 45,
            642, 105,
            642, 690,
            fill="#0a2340",
            outline="#4ed7ff",
            width=4,
        )
        c.create_rectangle(570, 125, 642, 680, fill="#102b4a", outline="#5c7da3", width=2)
        c.create_text(607, 430, text="LAUNCH", angle=90, fill="#6888ab", font=("Consolas", 14, "bold"))

        # 장식
        c.create_text(
            330, 85, text="NEBULA-7", fill="#ff75c8", font=("Consolas", 21, "bold")
        )
        c.create_arc(
            115, 95, 545, 395,
            start=20, extent=140,
            style="arc", outline="#214d70", width=2
        )
        c.create_arc(
            135, 115, 525, 375,
            start=18, extent=144,
            style="arc", outline="#173c5c", width=2
        )

        # 고정 벽 세그먼트
        self.walls = [
            Segment(Vec2(38, 690), Vec2(38, 115)),
            Segment(Vec2(38, 115), Vec2(92, 48)),
            Segment(Vec2(92, 48), Vec2(566, 48)),
            Segment(Vec2(566, 48), Vec2(642, 108)),
            Segment(Vec2(642, 108), Vec2(642, 690)),
            Segment(Vec2(570, 150), Vec2(570, 675), 0.9),
            Segment(Vec2(570, 150), Vec2(520, 110), 0.92, 35),
            Segment(Vec2(70, 510), Vec2(205, 650), 0.88),
            Segment(Vec2(590, 520), Vec2(475, 650), 0.88),
            Segment(Vec2(85, 470), Vec2(165, 545), 0.9, 15),
            Segment(Vec2(555, 465), Vec2(500, 530), 0.9, 15),
            Segment(Vec2(155, 550), Vec2(220, 585), 0.92, 20),
            Segment(Vec2(505, 545), Vec2(455, 585), 0.92, 20),
        ]

        # 벽 시각화
        for wall in self.walls:
            c.create_line(
                wall.a.x, wall.a.y, wall.b.x, wall.b.y,
                fill="#55cdf5", width=4, capstyle=tk.ROUND
            )

        # 범퍼
        self.bumpers = [
            Bumper(Vec2(205, 225), 34, 100),
            Bumper(Vec2(335, 170), 38, 100),
            Bumper(Vec2(470, 240), 34, 100),
            Bumper(Vec2(315, 320), 31, 100),
        ]

        for bumper in self.bumpers:
            x, y, r = bumper.center.x, bumper.center.y, bumper.radius
            c.create_oval(x-r-8, y-r-8, x+r+8, y+r+8, outline="#a248df", width=3)
            bumper.canvas_id = c.create_oval(
                x-r, y-r, x+r, y+r,
                fill="#67278e", outline="#f1a4ff", width=4
            )
            c.create_oval(x-11, y-11, x+11, y+11, fill="#ffd25e", outline="")
            c.create_text(x, y+r+21, text="+100", fill="#b9a7d8", font=("Consolas", 9, "bold"))

        # 사이드 타깃
        self.targets = [
            Bumper(Vec2(115, 315), 15, 250),
            Bumper(Vec2(535, 335), 15, 250),
            Bumper(Vec2(135, 405), 15, 250),
            Bumper(Vec2(520, 415), 15, 250),
        ]
        for target in self.targets:
            x, y, r = target.center.x, target.center.y, target.radius
            target.canvas_id = c.create_oval(
                x-r, y-r, x+r, y+r,
                fill="#1b6f82", outline="#77f4ff", width=3
            )
            c.create_text(x, y, text="★", fill="#eaffff", font=("Arial", 10, "bold"))

        # 하단 가이드와 드레인
        c.create_polygon(60, 535, 195, 666, 220, 630, 80, 495, fill="#153a5d", outline="#4ed7ff", width=2)
        c.create_polygon(590, 535, 470, 666, 445, 630, 570, 495, fill="#153a5d", outline="#4ed7ff", width=2)
        c.create_text(335, 680, text="▼  DRAIN  ▼", fill="#ff638d", font=("Consolas", 12, "bold"))

        self.left_flipper_item = c.create_line(0, 0, 0, 0, fill="#ffcf4a", width=19, capstyle=tk.ROUND)
        self.right_flipper_item = c.create_line(0, 0, 0, 0, fill="#ffcf4a", width=19, capstyle=tk.ROUND)

        # 플리퍼 축
        for pivot in (self.left_flipper.pivot, self.right_flipper.pivot):
            c.create_oval(
                pivot.x - 12, pivot.y - 12, pivot.x + 12, pivot.y + 12,
                fill="#ff6c9d", outline="#ffe3ee", width=3
            )

        self.ball_item = c.create_oval(0, 0, 0, 0, fill="#f6fbff", outline="#9ccfff", width=2)

    def bind_keys(self):
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.focus_force()

    def on_key_press(self, event):
        key = event.keysym.lower()
        if key in self.keys_down:
            return
        self.keys_down.add(key)

        if key in ("a", "left"):
            self.left_flipper.pressed = True
        elif key in ("d", "right"):
            self.right_flipper.pressed = True
        elif key == "space":
            self.start_charging()
        elif key == "r":
            self.restart_game()
        elif key == "escape":
            self.root.destroy()

    def on_key_release(self, event):
        key = event.keysym.lower()
        self.keys_down.discard(key)

        if key in ("a", "left"):
            self.left_flipper.pressed = False
        elif key in ("d", "right"):
            self.right_flipper.pressed = False
        elif key == "space":
            self.release_launch()

    def start_charging(self):
        if self.game_over or not self.ball_ready or self.charging:
            return

        self.charging = True
        self.charge_started = time.perf_counter()
        self.launch_power = 0.12
        self.message = "발사 세기 충전 중... 12%"

    def release_launch(self):
        if not self.charging or self.game_over or not self.ball_ready:
            return

        held_time = time.perf_counter() - self.charge_started
        self.launch_power = max(
            0.12,
            min(1.0, held_time / self.charge_time_max),
        )
        self.charging = False
        self.launch_ball(self.launch_power)

    def launch_ball(self, power: float):
        if self.game_over or not self.ball_ready:
            return

        self.launch_power = max(0.12, min(1.0, power))
        self.ball_ready = False
        self.launching = True
        self.launch_elapsed = 0.0

        # 강할수록 발사 레인을 더 빠르게 통과한다.
        self.launch_duration = 1.15 - 0.58 * self.launch_power
        self.ball_vel = Vec2(0.0, 0.0)
        self.show_message(f"발사 세기 {round(self.launch_power * 100)}%!", 0.8)

    def restart_game(self):
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.left_flipper.pressed = False
        self.right_flipper.pressed = False
        self.reset_ball()
        self.show_message("새 게임! SPACE 키로 발사", 1.5)

    def reset_ball(self):
        self.ball_ready = True
        self.launching = False
        self.launch_elapsed = 0.0
        self.charging = False
        self.charge_started = 0.0
        self.launch_power = 0.0
        self.ball_pos = Vec2(610.0, 625.0)
        self.ball_vel = Vec2(0.0, 0.0)

    def show_message(self, text: str, seconds: float):
        self.message = text
        self.message_until = time.perf_counter() + seconds

    def loop(self):
        now = time.perf_counter()
        dt = min(now - self.last_time, 0.025)
        self.last_time = now

        self.update(dt, now)
        self.draw_dynamic()
        self.root.after(FPS_DELAY_MS, self.loop)

    def update(self, dt: float, now: float):
        self.left_flipper.update(dt)
        self.right_flipper.update(dt)

        # Space 키를 누르는 동안 12%에서 100%까지 충전한다.
        if self.charging and self.ball_ready and not self.game_over:
            held_time = now - self.charge_started
            self.launch_power = max(
                0.12,
                min(1.0, held_time / self.charge_time_max),
            )
            self.message = f"발사 세기 충전 중... {round(self.launch_power * 100)}%"

        if not self.game_over and not self.ball_ready:
            # 발사 중에는 물리 충돌에 맡기지 않고, 발사 레인을 따라가는
            # 짧은 고정 궤적을 사용한다. 이렇게 하면 PC 속도나 프레임에
            # 관계없이 공이 반드시 중앙 플레이필드로 진입한다.
            if self.launching:
                self.launch_elapsed += dt
                progress = min(self.launch_elapsed / self.launch_duration, 1.0)

                if progress < 0.78:
                    lane_progress = progress / 0.78
                    self.ball_pos = Vec2(
                        610.0,
                        625.0 + (105.0 - 625.0) * lane_progress,
                    )
                else:
                    curve_progress = (progress - 0.78) / 0.22
                    self.ball_pos = Vec2(
                        610.0 + (500.0 - 610.0) * curve_progress,
                        105.0 - math.sin(curve_progress * math.pi) * 18.0
                        + 22.0 * curve_progress,
                    )

                if progress >= 1.0:
                    self.launching = False
                    self.ball_pos = Vec2(500.0, 125.0)

                    # 약하게 발사하면 중앙 근처로 천천히 떨어지고,
                    # 강하게 발사하면 왼쪽 깊숙한 곳까지 빠르게 진행한다.
                    horizontal_speed = -(220.0 + 310.0 * self.launch_power)
                    downward_speed = 260.0 - 175.0 * self.launch_power
                    self.ball_vel = Vec2(horizontal_speed, downward_speed)
                    self.show_message(
                        f"플레이필드 진입! 세기 {round(self.launch_power * 100)}%",
                        0.7,
                    )

            else:
                # 공의 속도가 빠를수록 한 프레임의 이동을 더 잘게 나눈다.
                # 기존 코드는 위치를 한 번에 이동한 뒤 충돌만 반복해서,
                # 공이 얇은 벽을 통째로 건너뛰는 터널링 현상이 생길 수 있었다.
                self.update_ball_physics(dt)

                # 공이 아래쪽 드레인으로 빠진 경우에만 목숨을 잃는다.
                if self.ball_pos.y > HEIGHT + 30:
                    self.lose_ball()

        # 범퍼 점멸 해제
        for bumper in self.bumpers + self.targets:
            if bumper.canvas_id is None:
                continue
            if now < bumper.flash_until:
                fill = "#fff08a" if bumper in self.bumpers else "#ffffff"
            else:
                fill = "#67278e" if bumper in self.bumpers else "#1b6f82"
            self.canvas.itemconfigure(bumper.canvas_id, fill=fill)

        if self.game_over:
            self.message = "GAME OVER\nR 키로 다시 시작"
        elif self.charging:
            self.message = f"발사 세기 충전 중... {round(self.launch_power * 100)}%"
        elif self.ball_ready and now > self.message_until:
            self.message = "SPACE를 누르고 있다가 놓으세요"
        elif now > self.message_until and not self.ball_ready:
            self.message = "플리퍼로 공을 살려내세요!"

    def update_ball_physics(self, dt: float):
        """빠른 공이 벽을 통과하지 않도록 이동과 충돌을 서브스텝으로 계산한다."""
        speed = self.ball_vel.length()
        predicted_travel = speed * dt + 0.5 * GRAVITY * dt * dt

        # 한 번의 이동 거리를 공 반지름의 약 45% 이하로 제한한다.
        # 너무 많은 계산이 생기지 않도록 최대 12단계까지만 사용한다.
        max_travel_per_step = BALL_RADIUS * 0.45
        substeps = max(
            1,
            min(12, math.ceil(predicted_travel / max_travel_per_step)),
        )
        step_dt = dt / substeps

        for _ in range(substeps):
            self.ball_vel.y += GRAVITY * step_dt
            self.ball_pos.x += self.ball_vel.x * step_dt
            self.ball_pos.y += self.ball_vel.y * step_dt

            # 겹침이 큰 경우를 대비해 같은 위치에서 충돌을 두 번 정리한다.
            for _ in range(2):
                for wall in self.walls:
                    self.collide_segment(wall)

                self.collide_flipper(self.left_flipper)
                self.collide_flipper(self.right_flipper)

                for bumper in self.bumpers:
                    self.collide_circle(bumper, boost=285.0)
                for target in self.targets:
                    self.collide_circle(target, boost=135.0)

            # 수치 오차나 매우 강한 충돌로 외벽을 넘더라도
            # 드레인을 제외한 방향으로는 테이블 밖으로 나가지 않게 한다.
            self.keep_ball_inside_table()

            speed = self.ball_vel.length()
            max_speed = 1150.0
            if speed > max_speed:
                self.ball_vel = self.ball_vel * (max_speed / speed)

            if self.ball_pos.y > HEIGHT + 30:
                break

    def keep_ball_inside_table(self):
        """테이블 외곽을 넘은 공을 안쪽으로 되돌리는 최종 안전장치."""
        # y=690 아래는 정상적인 드레인 구간이므로 막지 않는다.
        if self.ball_pos.y > 690.0:
            return

        margin = BALL_RADIUS + 1.5

        # 상단을 넘어가는 것을 방지한다.
        safe_top = 48.0 + margin
        if self.ball_pos.y < safe_top:
            self.ball_pos.y = safe_top
            if self.ball_vel.y < 0.0:
                self.ball_vel.y = abs(self.ball_vel.y) * 0.84

        y = self.ball_pos.y

        # 왼쪽 위 사선: (38, 115) -> (92, 48)
        if y < 115.0:
            ratio = max(0.0, min(1.0, (115.0 - y) / 67.0))
            left_edge = 38.0 + 54.0 * ratio
        else:
            left_edge = 38.0

        # 오른쪽 위 사선: (566, 48) -> (642, 108)
        if y < 108.0:
            ratio = max(0.0, min(1.0, (y - 48.0) / 60.0))
            right_edge = 566.0 + 76.0 * ratio
        else:
            right_edge = 642.0

        safe_left = left_edge + margin
        safe_right = right_edge - margin

        if self.ball_pos.x < safe_left:
            self.ball_pos.x = safe_left
            if self.ball_vel.x < 0.0:
                self.ball_vel.x = abs(self.ball_vel.x) * 0.84

        if self.ball_pos.x > safe_right:
            self.ball_pos.x = safe_right
            if self.ball_vel.x > 0.0:
                self.ball_vel.x = -abs(self.ball_vel.x) * 0.84

    def lose_ball(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.game_over = True
            self.ball_ready = False
            self.ball_vel = Vec2(0.0, 0.0)
            self.ball_pos = Vec2(-100, -100)
            self.high_score = max(self.high_score, self.score)
        else:
            self.reset_ball()
            self.show_message(f"공을 잃었습니다! 남은 공 {self.lives}개", 1.5)

    def collide_segment(self, segment: Segment):
        closest, t = self.closest_point_on_segment(self.ball_pos, segment.a, segment.b)
        offset = self.ball_pos - closest
        distance = offset.length()

        if distance >= BALL_RADIUS:
            return

        if distance < 1e-6:
            wall_dir = segment.b - segment.a
            normal = Vec2(-wall_dir.y, wall_dir.x).normalized()
        else:
            normal = offset * (1.0 / distance)

        penetration = BALL_RADIUS - distance
        self.ball_pos = self.ball_pos + normal * (penetration + 0.7)

        normal_speed = self.ball_vel.dot(normal)
        if normal_speed < 0:
            self.ball_vel = self.ball_vel - normal * ((1.0 + segment.restitution) * normal_speed)
            if segment.boost:
                self.ball_vel = self.ball_vel + normal * segment.boost

    def collide_flipper(self, flipper: Flipper):
        a = flipper.pivot
        b = flipper.tip
        closest, t = self.closest_point_on_segment(self.ball_pos, a, b)
        offset = self.ball_pos - closest
        distance = offset.length()
        effective_radius = BALL_RADIUS + 10.0

        if distance >= effective_radius:
            return

        if distance < 1e-6:
            direction = b - a
            normal = Vec2(-direction.y, direction.x).normalized()
        else:
            normal = offset * (1.0 / distance)

        penetration = effective_radius - distance
        self.ball_pos = self.ball_pos + normal * (penetration + 1.0)

        arm = closest - flipper.pivot
        surface_velocity = Vec2(
            -flipper.angular_velocity * arm.y,
            flipper.angular_velocity * arm.x,
        )
        relative_velocity = self.ball_vel - surface_velocity
        normal_speed = relative_velocity.dot(normal)

        if normal_speed < 0:
            restitution = 0.92
            relative_velocity = relative_velocity - normal * ((1.0 + restitution) * normal_speed)
            self.ball_vel = relative_velocity + surface_velocity

            if flipper.pressed:
                extra = 170.0 + abs(flipper.angular_velocity) * 22.0
                self.ball_vel = self.ball_vel + normal * extra

    def collide_circle(self, obstacle: Bumper, boost: float):
        offset = self.ball_pos - obstacle.center
        distance = offset.length()
        minimum = BALL_RADIUS + obstacle.radius

        if distance >= minimum:
            return

        normal = offset.normalized()
        penetration = minimum - distance
        self.ball_pos = self.ball_pos + normal * (penetration + 0.8)

        normal_speed = self.ball_vel.dot(normal)
        if normal_speed < 0:
            self.ball_vel = self.ball_vel - normal * (1.92 * normal_speed)
            self.ball_vel = self.ball_vel + normal * boost

            now = time.perf_counter()
            if now >= obstacle.flash_until:
                self.score += obstacle.score
                self.high_score = max(self.high_score, self.score)
                obstacle.flash_until = now + 0.12

    @staticmethod
    def closest_point_on_segment(point: Vec2, a: Vec2, b: Vec2):
        ab = b - a
        denominator = ab.dot(ab)
        if denominator < 1e-9:
            return a, 0.0

        t = (point - a).dot(ab) / denominator
        t = max(0.0, min(1.0, t))
        return a + ab * t, t

    def draw_dynamic(self):
        lp = self.left_flipper.pivot
        lt = self.left_flipper.tip
        rp = self.right_flipper.pivot
        rt = self.right_flipper.tip

        self.canvas.coords(self.left_flipper_item, lp.x, lp.y, lt.x, lt.y)
        self.canvas.coords(self.right_flipper_item, rp.x, rp.y, rt.x, rt.y)

        x, y = self.ball_pos.x, self.ball_pos.y
        r = BALL_RADIUS
        self.canvas.coords(self.ball_item, x-r, y-r, x+r, y+r)

        self.canvas.itemconfigure(self.score_item, text=f"{self.score:06d}")
        self.canvas.itemconfigure(
            self.lives_item,
            text=" ".join("●" for _ in range(self.lives)) or "—",
        )

        power = max(0.0, min(1.0, self.launch_power))
        bar_left = 703
        bar_right = bar_left + 154 * power
        self.canvas.coords(self.power_bar_item, bar_left, 339, bar_right, 353)
        self.canvas.itemconfigure(
            self.power_text_item,
            text=f"{round(power * 100)}%",
        )
        self.canvas.itemconfigure(self.status_item, text=self.message)


def main():
    root = tk.Tk()
    RetroPinball(root)
    root.mainloop()


if __name__ == "__main__":
    main()
