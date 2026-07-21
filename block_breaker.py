import math
import random
import tkinter as tk


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 680
FIELD_WIDTH = 700
FPS_DELAY = 16

PADDLE_WIDTH = 120
PADDLE_HEIGHT = 16
PADDLE_Y = 620
PADDLE_SPEED = 9

BALL_RADIUS = 9
BALL_SPEED = 14.0

BRICK_ROWS = 6
BRICK_COLS = 10
BRICK_GAP = 6
BRICK_TOP = 80
BRICK_LEFT = 35
BRICK_HEIGHT = 28
BRICK_COLORS = ["#ff6b6b", "#ff9f43", "#ffd166", "#6be7c8", "#5b7cff", "#c56bff"]


class BlockBreaker:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Block Breaker")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="#0e1320",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.keys_down = set()
        self.after_id = None
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False

        self.paddle_x = (FIELD_WIDTH - PADDLE_WIDTH) / 2
        self.paddle_y = PADDLE_Y
        self.ball_x = FIELD_WIDTH / 2
        self.ball_y = PADDLE_Y - BALL_RADIUS - 1
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.ball_stuck = True

        self.bricks = []

        self.draw_static_ui()
        self.bind_keys()
        self.reset_round()
        self.loop()

    def draw_static_ui(self):
        c = self.canvas

        c.create_rectangle(0, 0, FIELD_WIDTH, WINDOW_HEIGHT, fill="#111827", outline="#24324a")
        c.create_rectangle(FIELD_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#0b1020", outline="#24324a")

        c.create_text(
            800,
            55,
            text="BLOCK\nBREAKER",
            fill="#f7fbff",
            font=("Consolas", 24, "bold"),
            justify="center",
        )

        c.create_text(800, 140, text="SCORE", fill="#9db1d6", font=("Consolas", 14, "bold"))
        self.score_text = c.create_text(800, 178, text="000000", fill="#ffe08a", font=("Consolas", 28, "bold"))

        c.create_text(800, 235, text="LIVES", fill="#9db1d6", font=("Consolas", 14, "bold"))
        self.lives_text = c.create_text(800, 273, text="● ● ●", fill="#ff8bc6", font=("Consolas", 20, "bold"))

        c.create_text(800, 350, text="CONTROLS", fill="#9db1d6", font=("Consolas", 14, "bold"))
        c.create_text(
            800,
            395,
            text=(
                "Left / Right  Move\n"
                "Space         Launch\n"
                "R             Restart\n"
                "Esc           Quit"
            ),
            fill="#d9e4ff",
            font=("Consolas", 11),
            justify="left",
        )

        c.create_text(800, 560, text="Break all bricks", fill="#8fb2ff", font=("Consolas", 12, "bold"))
        self.message_text = c.create_text(
            800,
            610,
            text="SPACE로 시작",
            fill="#ffcd67",
            font=("Consolas", 12, "bold"),
            width=180,
            justify="center",
        )

    def bind_keys(self):
        self.root.bind("<KeyPress-Left>", lambda event: self.keys_down.add("Left"))
        self.root.bind("<KeyRelease-Left>", lambda event: self.keys_down.discard("Left"))
        self.root.bind("<KeyPress-Right>", lambda event: self.keys_down.add("Right"))
        self.root.bind("<KeyRelease-Right>", lambda event: self.keys_down.discard("Right"))
        self.root.bind("<KeyPress-a>", lambda event: self.keys_down.add("Left"))
        self.root.bind("<KeyRelease-a>", lambda event: self.keys_down.discard("Left"))
        self.root.bind("<KeyPress-d>", lambda event: self.keys_down.add("Right"))
        self.root.bind("<KeyRelease-d>", lambda event: self.keys_down.discard("Right"))
        self.root.bind("<space>", lambda event: self.launch_ball())
        self.root.bind("<r>", lambda event: self.restart())
        self.root.bind("<R>", lambda event: self.restart())
        self.root.bind("<Escape>", lambda event: self.root.destroy())

    def restart(self):
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.win = False
        self.keys_down.clear()
        self.paddle_x = (FIELD_WIDTH - PADDLE_WIDTH) / 2
        self.reset_round()
        self.canvas.itemconfigure(self.message_text, text="SPACE로 시작")

    def reset_round(self):
        self.ball_stuck = True
        self.ball_x = self.paddle_x + PADDLE_WIDTH / 2
        self.ball_y = self.paddle_y - BALL_RADIUS - 1
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.create_bricks()
        self.redraw()

    def create_bricks(self):
        self.bricks = []
        brick_width = (FIELD_WIDTH - 2 * BRICK_LEFT - (BRICK_COLS - 1) * BRICK_GAP) / BRICK_COLS

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x1 = BRICK_LEFT + col * (brick_width + BRICK_GAP)
                y1 = BRICK_TOP + row * (BRICK_HEIGHT + BRICK_GAP)
                brick = {
                    "x1": x1,
                    "y1": y1,
                    "x2": x1 + brick_width,
                    "y2": y1 + BRICK_HEIGHT,
                    "color": BRICK_COLORS[row % len(BRICK_COLORS)],
                    "alive": True,
                }
                self.bricks.append(brick)

    def launch_ball(self):
        if self.game_over or self.win:
            return
        if self.ball_stuck:
            angle = random.uniform(math.radians(40), math.radians(140))
            if 0.5 < math.cos(angle):
                angle = math.pi - angle
            self.ball_vx = math.cos(angle) * BALL_SPEED
            self.ball_vy = -abs(math.sin(angle) * BALL_SPEED)
            self.ball_stuck = False
            self.canvas.itemconfigure(self.message_text, text="")

    def update_paddle(self):
        if "Left" in self.keys_down:
            self.paddle_x -= PADDLE_SPEED
        if "Right" in self.keys_down:
            self.paddle_x += PADDLE_SPEED

        self.paddle_x = max(0, min(FIELD_WIDTH - PADDLE_WIDTH, self.paddle_x))

        if self.ball_stuck:
            self.ball_x = self.paddle_x + PADDLE_WIDTH / 2

    def update_ball(self):
        if self.ball_stuck or self.game_over or self.win:
            return

        next_x = self.ball_x + self.ball_vx
        next_y = self.ball_y + self.ball_vy

        if next_x - BALL_RADIUS <= 0:
            next_x = BALL_RADIUS
            self.ball_vx *= -1
        elif next_x + BALL_RADIUS >= FIELD_WIDTH:
            next_x = FIELD_WIDTH - BALL_RADIUS
            self.ball_vx *= -1

        if next_y - BALL_RADIUS <= 0:
            next_y = BALL_RADIUS
            self.ball_vy *= -1

        if next_y - BALL_RADIUS > WINDOW_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
                self.canvas.itemconfigure(self.message_text, text="GAME OVER - R to restart")
                return
            self.canvas.itemconfigure(self.message_text, text="한 목숨 감소 - SPACE로 재시작")
            self.reset_round()
            return

        self.handle_paddle_collision(next_x, next_y)
        self.handle_brick_collision(next_x, next_y)

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy

    def handle_paddle_collision(self, next_x, next_y):
        if self.ball_vy > 0:
            paddle_left = self.paddle_x
            paddle_right = self.paddle_x + PADDLE_WIDTH
            paddle_top = self.paddle_y
            paddle_bottom = self.paddle_y + PADDLE_HEIGHT

            if (
                next_x + BALL_RADIUS >= paddle_left
                and next_x - BALL_RADIUS <= paddle_right
                and next_y + BALL_RADIUS >= paddle_top
                and next_y - BALL_RADIUS <= paddle_bottom
            ):
                offset = (next_x - (self.paddle_x + PADDLE_WIDTH / 2)) / (PADDLE_WIDTH / 2)
                offset = max(-1.0, min(1.0, offset))
                speed = max(BALL_SPEED, math.hypot(self.ball_vx, self.ball_vy))
                self.ball_vx = offset * speed
                self.ball_vy = -abs(math.sqrt(max(0.0, speed * speed - self.ball_vx * self.ball_vx)))
                self.ball_y = self.paddle_y - BALL_RADIUS - 1
                self.score += 5

    def handle_brick_collision(self, next_x, next_y):
        for brick in self.bricks:
            if not brick["alive"]:
                continue

            if (
                next_x + BALL_RADIUS >= brick["x1"]
                and next_x - BALL_RADIUS <= brick["x2"]
                and next_y + BALL_RADIUS >= brick["y1"]
                and next_y - BALL_RADIUS <= brick["y2"]
            ):
                brick["alive"] = False
                self.score += 10

                overlap_left = abs((self.ball_x + BALL_RADIUS) - brick["x1"])
                overlap_right = abs((brick["x2"] - BALL_RADIUS) - self.ball_x)
                overlap_top = abs((self.ball_y + BALL_RADIUS) - brick["y1"])
                overlap_bottom = abs((brick["y2"] - BALL_RADIUS) - self.ball_y)
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                if min_overlap in (overlap_left, overlap_right):
                    self.ball_vx *= -1
                else:
                    self.ball_vy *= -1

                break

        if all(not brick["alive"] for brick in self.bricks):
            self.win = True
            self.canvas.itemconfigure(self.message_text, text="YOU WIN! - R to play again")

    def redraw(self):
        self.canvas.delete("play")

        for brick in self.bricks:
            if brick["alive"]:
                self.canvas.create_rectangle(
                    brick["x1"],
                    brick["y1"],
                    brick["x2"],
                    brick["y2"],
                    fill=brick["color"],
                    outline="#182033",
                    tags="play",
                )

        self.canvas.create_rectangle(
            self.paddle_x,
            self.paddle_y,
            self.paddle_x + PADDLE_WIDTH,
            self.paddle_y + PADDLE_HEIGHT,
            fill="#e8f0ff",
            outline="#ffffff",
            tags="play",
        )

        self.canvas.create_oval(
            self.ball_x - BALL_RADIUS,
            self.ball_y - BALL_RADIUS,
            self.ball_x + BALL_RADIUS,
            self.ball_y + BALL_RADIUS,
            fill="#fffbcc",
            outline="#fff2a8",
            tags="play",
        )

        self.canvas.itemconfigure(self.score_text, text=f"{self.score:06d}")
        self.canvas.itemconfigure(self.lives_text, text="● " * self.lives)

    def loop(self):
        if not self.game_over and not self.win:
            self.update_paddle()
            self.update_ball()
            self.redraw()
        self.after_id = self.root.after(FPS_DELAY, self.loop)


def main():
    root = tk.Tk()
    BlockBreaker(root)
    root.mainloop()


if __name__ == "__main__":
    main()