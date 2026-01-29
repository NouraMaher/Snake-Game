import pygame
import sys
import random
import time
import os
from collections import deque
import heapq

# =============[ SETTINGS ]=================
CELL_SIZE = 24
GRID_W = 20
GRID_H = 20

BOARD_W = GRID_W * CELL_SIZE
BOARD_H = GRID_H * CELL_SIZE

PANEL_H = 160
WINDOW_W = BOARD_W * 2
WINDOW_H = BOARD_H + PANEL_H

FPS = 16
RACE_TIME_LIMIT = 60.0  # مدة السباق بالثواني

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (70, 70, 70)
GREEN = (0, 200, 0)
RED = (230, 60, 60)
YELLOW = (255, 240, 0)
BLUE = (60, 130, 255)
PURPLE = (190, 60, 210)
DARK = (22, 22, 26)
DARK2 = (35, 35, 45)
BORDER = (200, 200, 200)


# =============[ PATHFINDING ]=================
def get_neighbors(node):
    x, y = node
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    res = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
            res.append((nx, ny))
    return res


def bfs(start, goal, blocked):
    q = deque([start])
    visited = {start}
    parent = {start: None}
    expanded = 0

    while q:
        cur = q.popleft()
        expanded += 1

        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path, expanded

        for nb in get_neighbors(cur):
            if nb not in visited and nb not in blocked:
                visited.add(nb)
                parent[nb] = cur
                q.append(nb)

    return None, expanded


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, blocked):
    pq = []
    heapq.heappush(pq, (0, 0, start))
    g = {start: 0}
    parent = {start: None}
    expanded = 0

    while pq:
        f, cost, cur = heapq.heappop(pq)
        expanded += 1

        if cur == goal:
            path = []
            while cur:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path, expanded

        for nb in get_neighbors(cur):
            if nb in blocked:
                continue
            new_g = cost + 1
            if nb not in g or new_g < g[nb]:
                g[nb] = new_g
                parent[nb] = cur
                heapq.heappush(pq, (new_g + heuristic(nb, goal), new_g, nb))

    return None, expanded


# =============[ SNAKE BOARD CLASS ]=================
class SnakeBoard:
    def __init__(self, algo, offset_x):
        self.algo = algo
        self.offset_x = offset_x
        self.reset()

    def reset(self):
        self.snake = [(GRID_W // 2, GRID_H // 2)]
        self.direction = (1, 0)
        self.alive = True
        self.foods = 0
        self.nodes_expanded = 0
        self.start_time = time.time()
        self.death_time = None

        self.spawn_food()

    def spawn_food(self):
        while True:
            fx = random.randint(0, GRID_W - 1)
            fy = random.randint(0, GRID_H - 1)
            if (fx, fy) not in self.snake:
                self.food = (fx, fy)
                break

    def choose_move(self):
        head = self.snake[0]
        blocked = set(self.snake[1:])

        if self.algo == "BFS":
            path, expanded = bfs(head, self.food, blocked)
        else:
            path, expanded = astar(head, self.food, blocked)

        self.nodes_expanded += expanded

        if path and len(path) > 1:
            next_cell = path[1]
            dx = next_cell[0] - head[0]
            dy = next_cell[1] - head[1]
            return dx, dy

        # Fallback: أي حركة آمنة
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = head[0] + dx, head[1] + dy
            if (0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in blocked):
                return dx, dy

        return self.direction

    def update(self):
        if not self.alive:
            return

        self.direction = self.choose_move()
        head = self.snake[0]
        dx, dy = self.direction
        nx, ny = head[0] + dx, head[1] + dy

        # collision
        if not (0 <= nx < GRID_W and 0 <= ny < GRID_H) or (nx, ny) in self.snake:
            self.alive = False
            self.death_time = time.time()
            return

        self.snake.insert(0, (nx, ny))

        if (nx, ny) == self.food:
            self.foods += 1
            self.spawn_food()
        else:
            self.snake.pop()

    def alive_time(self):
        if self.death_time is None:
            return time.time() - self.start_time
        return self.death_time - self.start_time

    def draw(self, screen):
        # خلفية خفيفة للوحة
        bg_rect = pygame.Rect(self.offset_x, 0, BOARD_W, BOARD_H)
        pygame.draw.rect(screen, DARK2, bg_rect)

        # grid
        for x in range(GRID_W):
            for y in range(GRID_H):
                rect = pygame.Rect(
                    self.offset_x + x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                pygame.draw.rect(screen, GRAY, rect, 1)

        # snake
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(
                self.offset_x + x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            if i == 0:
                pygame.draw.rect(screen, YELLOW, rect, border_radius=4)
            else:
                pygame.draw.rect(screen, GREEN, rect, border_radius=4)

        # food
        fx, fy = self.food
        rect = pygame.Rect(
            self.offset_x + fx * CELL_SIZE,
            fy * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )
        pygame.draw.rect(screen, RED, rect, border_radius=4)

        # border حول اللوحة
        pygame.draw.rect(screen, BORDER, bg_rect, 3, border_radius=6)


# =============[ RACE GAME CLASS ]=================
class RaceGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake AI Race - BFS vs A* (Timer & Results)")

        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.smallfont = pygame.font.SysFont("consolas", 16)
        self.bigfont = pygame.font.SysFont("consolas", 36, bold=True)
        self.midfont = pygame.font.SysFont("consolas", 28, bold=True)

        self.state = "MENU"
        self.btn_start = pygame.Rect(WINDOW_W // 2 - 120, WINDOW_H // 2 - 40, 240, 60)
        self.btn_exit = pygame.Rect(WINDOW_W // 2 - 120, WINDOW_H // 2 + 40, 240, 60)

        self.seed = int(time.time())
        self.race_start = None
        self.race_end_time = None
        self.last_results = None

    # ---------- Race control ----------
    def start_race(self):
        # نفس الـ seed للاتنين عشان الظروف متشابهة
        random.seed(self.seed)
        self.bfs_board = SnakeBoard("BFS", 0)

        random.seed(self.seed)
        self.astar_board = SnakeBoard("ASTAR", BOARD_W)

        now = time.time()
        self.bfs_board.start_time = now
        self.astar_board.start_time = now

        self.race_start = now
        self.race_end_time = None
        self.last_results = None
        self.state = "RACE"

    def finish_race(self):
        if self.race_end_time is not None:
            return  # already finished
        self.race_end_time = time.time()
        self.prepare_results()
        self.state = "RESULTS"

    def prepare_results(self):
        if self.race_start is None or self.race_end_time is None:
            return
        race_duration = min(self.race_end_time - self.race_start, RACE_TIME_LIMIT)

        bfs_foods = self.bfs_board.foods
        ast_foods = self.astar_board.foods

        bfs_alive = self.bfs_board.alive_time()
        ast_alive = self.astar_board.alive_time()

        bfs_nodes = self.bfs_board.nodes_expanded
        ast_nodes = self.astar_board.nodes_expanded

        self.last_results = {
            "seed": self.seed,
            "race_duration": race_duration,
            "bfs_foods": bfs_foods,
            "astar_foods": ast_foods,
            "bfs_alive": bfs_alive,
            "astar_alive": ast_alive,
            "bfs_nodes": bfs_nodes,
            "astar_nodes": ast_nodes,
        }

    def save_results_to_csv(self, filename="race_results.csv"):
        if not self.last_results:
            return
        file_exists = os.path.exists(filename)
        with open(filename, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write(
                    "timestamp,seed,race_duration,"
                    "bfs_foods,bfs_alive,bfs_nodes,"
                    "astar_foods,astar_alive,astar_nodes\n"
                )
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            r = self.last_results
            line = (
                f"{ts},{r['seed']},{r['race_duration']:.3f},"
                f"{r['bfs_foods']},{r['bfs_alive']:.3f},{r['bfs_nodes']},"
                f"{r['astar_foods']},{r['astar_alive']:.3f},{r['astar_nodes']}\n"
            )
            f.write(line)

    # ---------- Drawing helpers ----------
    def draw_text_center(self, text, font, color, y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WINDOW_W // 2, y))
        self.screen.blit(surf, rect)

    # ---------- MENU ----------
    def draw_menu(self):
        self.screen.fill(DARK)

        self.draw_text_center("Snake AI Race", self.bigfont, WHITE, 120)
        self.draw_text_center("BFS vs A*", self.midfont, PURPLE, 170)

        pygame.draw.rect(self.screen, PURPLE, self.btn_start, border_radius=12)
        pygame.draw.rect(self.screen, BLUE, self.btn_exit, border_radius=12)

        start_txt = self.font.render("START RACE", True, WHITE)
        exit_txt = self.font.render("EXIT", True, WHITE)

        self.screen.blit(start_txt, start_txt.get_rect(center=self.btn_start.center))
        self.screen.blit(exit_txt, exit_txt.get_rect(center=self.btn_exit.center))

        hint = "ESC to Quit"
        self.draw_text_center(hint, self.smallfont, GRAY, WINDOW_H - 40)

    # ---------- RACE ----------
    def update_race(self):
        self.bfs_board.update()
        self.astar_board.update()

        elapsed = time.time() - self.race_start
        both_dead = (not self.bfs_board.alive) and (not self.astar_board.alive)

        if elapsed >= RACE_TIME_LIMIT or both_dead:
            self.finish_race()

    def draw_labels_over_boards(self):
        # BFS label
        bfs_label = self.midfont.render("BFS", True, PURPLE)
        bfs_rect = bfs_label.get_rect(center=(BOARD_W // 2, 20))
        self.screen.blit(bfs_label, bfs_rect)

        # A* label
        ast_label = self.midfont.render("A*", True, BLUE)
        ast_rect = ast_label.get_rect(center=(BOARD_W + BOARD_W // 2, 20))
        self.screen.blit(ast_label, ast_rect)

    def draw_panel(self):
        panel_rect = pygame.Rect(0, BOARD_H, WINDOW_W, PANEL_H)
        pygame.draw.rect(self.screen, DARK2, panel_rect)

        # Timer
        if self.race_start is not None:
            if self.state == "RACE":
                elapsed = time.time() - self.race_start
            else:
                elapsed = self.last_results["race_duration"] if self.last_results else 0.0
        else:
            elapsed = 0.0

        time_left = max(0.0, RACE_TIME_LIMIT - elapsed)

        if self.state == "RACE":
            timer_text = f"Time Left: {time_left:.1f} s"
        else:
            timer_text = f"Race Time: {elapsed:.1f} s"

        self.screen.blit(
            self.font.render(timer_text, True, WHITE),
            (WINDOW_W // 2 - 90, BOARD_H + 10),
        )

        # BFS stats
        bfs_f = self.bfs_board.foods
        ast_f = self.astar_board.foods

        bfs_alive = self.bfs_board.alive_time()
        ast_alive = self.astar_board.alive_time()

        self.screen.blit(
            self.smallfont.render(
                f"BFS - Foods: {bfs_f} | Alive: {bfs_alive:.1f}s | Nodes: {self.bfs_board.nodes_expanded}",
                True,
                PURPLE,
            ),
            (20, BOARD_H + 40),
        )

        self.screen.blit(
            self.smallfont.render(
                f"A*  - Foods: {ast_f} | Alive: {ast_alive:.1f}s | Nodes: {self.astar_board.nodes_expanded}",
                True,
                BLUE,
            ),
            (20, BOARD_H + 65),
        )

        # Mini chart (leader)
        max_food = max(bfs_f, ast_f, 1)
        bar_w = 320
        bar_x = WINDOW_W // 2 - bar_w // 2
        bar_y = BOARD_H + 100

        pygame.draw.rect(self.screen, GRAY, pygame.Rect(bar_x, bar_y, bar_w, 20))
        bfs_w = int((bfs_f / max_food) * bar_w)
        ast_w = int((ast_f / max_food) * bar_w)

        pygame.draw.rect(self.screen, PURPLE, pygame.Rect(bar_x, bar_y, bfs_w, 20))
        pygame.draw.rect(self.screen, BLUE, pygame.Rect(bar_x, bar_y, ast_w, 20))

        # leader text
        if bfs_f > ast_f:
            leader = "Leader: BFS"
            color = PURPLE
        elif ast_f > bfs_f:
            leader = "Leader: A*"
            color = BLUE
        else:
            leader = "Leader: Draw"
            color = WHITE

        self.draw_text_center(leader, self.font, color, BOARD_H + 140)

        # إذا في وضع النتائج، نعرض تعليمات التحكم
        if self.state == "RESULTS":
            info = "R: Replay same  |  N: New race  |  S: Save results  |  M: Menu  |  ESC: Quit"
            self.draw_text_center(info, self.smallfont, WHITE, BOARD_H + PANEL_H - 20)

    def draw_race(self):
        self.screen.fill(DARK)
        self.bfs_board.draw(self.screen)
        self.astar_board.draw(self.screen)
        self.draw_labels_over_boards()
        self.draw_panel()

    # ---------- MAIN LOOP ----------
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # ESC يخرج في أي حالة
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if self.state == "MENU":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = event.pos
                        if self.btn_start.collidepoint(mx, my):
                            self.start_race()
                        elif self.btn_exit.collidepoint(mx, my):
                            pygame.quit()
                            sys.exit()

                elif self.state == "RESULTS":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # replay بنفس الـ seed
                            self.start_race()
                        elif event.key == pygame.K_n:
                            # new race بseed جديد
                            self.seed = int(time.time())
                            self.start_race()
                        elif event.key == pygame.K_s:
                            self.save_results_to_csv()
                        elif event.key == pygame.K_m:
                            self.state = "MENU"

            if self.state == "MENU":
                self.draw_menu()
            elif self.state in ("RACE", "RESULTS"):
                if self.state == "RACE":
                    self.update_race()
                self.draw_race()

            pygame.display.update()
            self.clock.tick(FPS)


# ========= RUN GAME ==========
if __name__ == "__main__":
    RaceGame().run()
