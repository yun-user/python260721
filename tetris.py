import random
import tkinter as tk


CELL_SIZE = 30
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
SIDE_PANEL = 220
WINDOW_WIDTH = BOARD_WIDTH * CELL_SIZE + SIDE_PANEL
WINDOW_HEIGHT = BOARD_HEIGHT * CELL_SIZE


COLORS = {
    "I": "#4dd9ff",
    "O": "#ffd84d",
    "T": "#c56bff",
    "S": "#62e36c",
    "Z": "#ff6b6b",
    "J": "#5b7cff",
    "L": "#ff9f43",
}


SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}


class TetrisGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Tetris")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="#0f1420",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.game_over = False
        self.drop_delay = 600
        self.after_id = None

        self.current_piece = None
        self.next_piece = self.make_piece()

        self.draw_static_ui()
        self.bind_keys()
        self.restart()

    def draw_static_ui(self):
        self.canvas.create_rectangle(
            0, 0, BOARD_WIDTH * CELL_SIZE, WINDOW_HEIGHT, fill="#111827", outline="#263247"
        )
        self.canvas.create_rectangle(
            BOARD_WIDTH * CELL_SIZE, 0, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#0b1020", outline="#263247"
        )

        self.canvas.create_text(
            BOARD_WIDTH * CELL_SIZE + 110,
            50,
            text="TETRIS",
            fill="#f5f7ff",
            font=("Consolas", 24, "bold"),
        )
        self.score_text = self.canvas.create_text(
            BOARD_WIDTH * CELL_SIZE + 20,
            115,
            anchor="w",
            text="Score: 0",
            fill="#d9e4ff",
            font=("Consolas", 13, "bold"),
        )
        self.lines_text = self.canvas.create_text(
            BOARD_WIDTH * CELL_SIZE + 20,
            145,
            anchor="w",
            text="Lines: 0",
            fill="#d9e4ff",
            font=("Consolas", 13, "bold"),
        )
        self.level_text = self.canvas.create_text(
            BOARD_WIDTH * CELL_SIZE + 20,
            175,
            anchor="w",
            text="Level: 1",
            fill="#d9e4ff",
            font=("Consolas", 13, "bold"),
        )

        self.canvas.create_text(
            BOARD_WIDTH * CELL_SIZE + 110,
            230,
            text="Next",
            fill="#9cb2d9",
            font=("Consolas", 14, "bold"),
        )

        self.canvas.create_rectangle(
            BOARD_WIDTH * CELL_SIZE + 40,
            250,
            WINDOW_WIDTH - 40,
            370,
            outline="#2c3e5f",
            width=2,
        )

        self.canvas.create_text(
            BOARD_WIDTH * CELL_SIZE + 110,
            402,
            text="Controls",
            fill="#9cb2d9",
            font=("Consolas", 14, "bold"),
        )
        self.canvas.create_text(
            BOARD_WIDTH * CELL_SIZE + 20,
            434,
            anchor="w",
            text=(
                "Left / Right : Move\n"
                "Up / X       : Rotate\n"
                "Down         : Soft drop\n"
                "Space        : Hard drop\n"
                "R            : Restart\n"
                "Esc          : Quit"
            ),
            fill="#d9e4ff",
            font=("Consolas", 10),
            justify="left",
        )

        self.message_text = self.canvas.create_text(
            BOARD_WIDTH * CELL_SIZE + 110,
            558,
            text="",
            fill="#ffcd67",
            font=("Consolas", 10, "bold"),
            width=180,
            justify="center",
        )

    def bind_keys(self):
        self.root.bind("<Left>", lambda event: self.move_piece(-1, 0))
        self.root.bind("<Right>", lambda event: self.move_piece(1, 0))
        self.root.bind("<Down>", lambda event: self.soft_drop())
        self.root.bind("<Up>", lambda event: self.rotate_piece())
        self.root.bind("<x>", lambda event: self.rotate_piece())
        self.root.bind("<X>", lambda event: self.rotate_piece())
        self.root.bind("<space>", lambda event: self.hard_drop())
        self.root.bind("<r>", lambda event: self.restart())
        self.root.bind("<R>", lambda event: self.restart())
        self.root.bind("<Escape>", lambda event: self.root.destroy())

    def make_piece(self):
        kind = random.choice(list(SHAPES.keys()))
        return {
            "kind": kind,
            "rotation": 0,
            "x": 3,
            "y": 0,
        }

    def get_cells(self, piece):
        blocks = SHAPES[piece["kind"]]
        pattern = blocks[piece["rotation"] % len(blocks)]
        return [(piece["x"] + dx, piece["y"] + dy) for dx, dy in pattern]

    def collision(self, piece, dx=0, dy=0, rotation=None):
        test_piece = dict(piece)
        test_piece["x"] += dx
        test_piece["y"] += dy
        if rotation is not None:
            test_piece["rotation"] = rotation

        for x, y in self.get_cells(test_piece):
            if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                return True
            if y >= 0 and self.board[y][x] is not None:
                return True
        return False

    def lock_piece(self):
        for x, y in self.get_cells(self.current_piece):
            if 0 <= y < BOARD_HEIGHT:
                self.board[y][x] = COLORS[self.current_piece["kind"]]

        cleared = self.clear_lines()
        if cleared:
            self.score += (cleared * cleared) * 100
            self.lines += cleared
            self.level = self.lines // 10 + 1
            self.drop_delay = max(120, 600 - (self.level - 1) * 45)

        self.current_piece = self.next_piece
        self.next_piece = self.make_piece()

        if self.collision(self.current_piece):
            self.game_over = True
            self.canvas.itemconfigure(self.message_text, text="Game Over - press R to restart")
            self.stop_loop()

    def clear_lines(self):
        remaining = []
        cleared = 0
        for row in self.board:
            if all(cell is not None for cell in row):
                cleared += 1
            else:
                remaining.append(row)

        for _ in range(cleared):
            remaining.insert(0, [None for _ in range(BOARD_WIDTH)])

        if cleared:
            self.board = remaining
        return cleared

    def move_piece(self, dx, dy):
        if self.game_over:
            return
        if not self.collision(self.current_piece, dx=dx, dy=dy):
            self.current_piece["x"] += dx
            self.current_piece["y"] += dy
            self.redraw()
            return True
        if dy == 1:
            self.lock_piece()
            self.redraw()
        return False

    def rotate_piece(self):
        if self.game_over:
            return
        next_rotation = (self.current_piece["rotation"] + 1) % len(SHAPES[self.current_piece["kind"]])
        for shift_x in (0, -1, 1, -2, 2):
            if not self.collision(self.current_piece, dx=shift_x, rotation=next_rotation):
                self.current_piece["rotation"] = next_rotation
                self.current_piece["x"] += shift_x
                self.redraw()
                return

    def soft_drop(self):
        if self.game_over:
            return
        if not self.move_piece(0, 1):
            return
        self.score += 1
        self.update_info()

    def hard_drop(self):
        if self.game_over:
            return
        drop_distance = 0
        while not self.collision(self.current_piece, dy=1):
            self.current_piece["y"] += 1
            drop_distance += 1
        self.score += drop_distance * 2
        self.lock_piece()
        self.redraw()
        self.update_info()

    def update_info(self):
        self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")
        self.canvas.itemconfigure(self.lines_text, text=f"Lines: {self.lines}")
        self.canvas.itemconfigure(self.level_text, text=f"Level: {self.level}")

    def redraw(self):
        self.canvas.delete("board")

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                color = self.board[y][x]
                if color is not None:
                    self.canvas.create_rectangle(
                        x * CELL_SIZE + 1,
                        y * CELL_SIZE + 1,
                        (x + 1) * CELL_SIZE - 1,
                        (y + 1) * CELL_SIZE - 1,
                        fill=color,
                        outline="#182033",
                        tags="board",
                    )

        if not self.game_over:
            for x, y in self.get_cells(self.current_piece):
                if y >= 0:
                    self.canvas.create_rectangle(
                        x * CELL_SIZE + 1,
                        y * CELL_SIZE + 1,
                        (x + 1) * CELL_SIZE - 1,
                        (y + 1) * CELL_SIZE - 1,
                        fill=COLORS[self.current_piece["kind"]],
                        outline="#ffffff",
                        width=1,
                        tags="board",
                    )

        self.canvas.delete("next_piece")
        preview_kind = self.next_piece["kind"]
        preview_cells = SHAPES[preview_kind][0]
        offset_x = BOARD_WIDTH * CELL_SIZE + 78
        offset_y = 280
        for dx, dy in preview_cells:
            self.canvas.create_rectangle(
                offset_x + dx * 22,
                offset_y + dy * 22,
                offset_x + dx * 22 + 20,
                offset_y + dy * 22 + 20,
                fill=COLORS[preview_kind],
                outline="#182033",
                tags="next_piece",
            )

        self.update_info()
        if self.game_over:
            self.canvas.itemconfigure(self.message_text, text="Game Over - press R to restart")
        else:
            self.canvas.itemconfigure(self.message_text, text="")

    def tick(self):
        if not self.game_over:
            self.move_piece(0, 1)
            self.redraw()
            if not self.game_over:
                self.after_id = self.root.after(self.drop_delay, self.tick)

    def stop_loop(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def restart(self):
        self.stop_loop()
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.drop_delay = 600
        self.game_over = False
        self.current_piece = self.make_piece()
        self.next_piece = self.make_piece()
        if self.collision(self.current_piece):
            self.current_piece["x"] = 3
            self.current_piece["y"] = 0
        self.redraw()
        self.after_id = self.root.after(self.drop_delay, self.tick)


def main():
    root = tk.Tk()
    TetrisGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()