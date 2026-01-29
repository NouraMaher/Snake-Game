import pygame
import sys
import random
from collections import deque
import heapq

# =============[ SETTINGS ]=================
CELL_SIZE = 32
GRID_W, GRID_H = 20, 20  # Grid width and height in cells

BOARD_W = GRID_W * CELL_SIZE
BOARD_H = GRID_H * CELL_SIZE

PANEL_H = 120
WINDOW_W = BOARD_W * 2        # Two boards: BFS (left) + A* (right)
WINDOW_H = BOARD_H + PANEL_H

FPS = 16  # Game update rate (frames per second)

# Colors (RGB)
WHITE  = (255, 255, 255)
GRAY   = (70, 70, 70)
GREEN  = (0, 200, 0)
RED    = (230, 60, 60)
YELLOW = (255, 240, 0)
BLUE   = (60, 130, 255)
PURPLE = (190, 60, 210)
DARK   = (22, 22, 26)
DARK2  = (35, 35, 45)
BORDER = (200, 200, 200)


# =============[ PATHFINDING UTILITIES ]=================
def get_neighbors(node):
    """Return all valid neighboring grid cells (4-directional movement)."""
    x, y = node
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    res = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
            res.append((nx, ny))
    return res


# =============[ BFS ALGORITHM ]=================
def bfs(start, goal, blocked):
    """
    Breadth-First Search:
    - Guarantees the shortest path in an unweighted grid.
    - Expands nodes layer by layer.
    """
    q = deque([start])
    visited = {start}
    parent = {start: None}
    expanded = 0

    while q:
        cur = q.popleft()
        expanded += 1

        if cur == goal:
            # Reconstruct path from goal → start
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


# =============[ A* ALGORITHM ]=================
def heuristic(a, b):
    """Manhattan distance heuristic suitable for grid pathfinding."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, blocked):
    """
    A* Search:
    - Uses f = g + h (cost + heuristic)
    - Usually expands fewer nodes than BFS.
    """
    pq = []  # priority queue: (f, g, node)
    heapq.heappush(pq, (0, 0, start))
    g = {start: 0}
    parent = {start: None}
    expanded = 0

    while pq:
        f, cost, cur = heapq.heappop(pq)
        expanded += 1

        if cur == goal:
            # Reconstruct path
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
                h = heuristic(nb, goal)
                heapq.heappush(pq, (new_g + h, new_g, nb))

    return None, expanded


# =============[ SNAKE BOARD CLASS : تنفذ الحركة وتكشف التصادم]=================
class SnakeBoard:
    """
    Handles:
    - Snake movement
    - Food spawning
    - Pathfinding calls
    - Rendering of the board
    """
    def __init__(self, algo, offset_x):
        self.algo = algo          # "BFS" or "A*"
        self.offset_x = offset_x  # Position of this board on the window
        self.reset()

    def reset(self):
        self.snake = [(GRID_W // 2, GRID_H // 2)]
        self.direction = (1, 0)
        self.alive = True
        self.foods = 0
        self.nodes_expanded = 0
        self.spawn_food()

    def spawn_food(self):
        """Spawn food in a random free cell."""
        while True:
            fx = random.randint(0, GRID_W - 1)
            fy = random.randint(0, GRID_H - 1)
            if (fx, fy) not in self.snake:
                self.food = (fx, fy)
                break

    def choose_move(self):
        """Use BFS or A* to select the snake’s next move."""
        head = self.snake[0]
        blocked = set(self.snake[1:])  # Snake body is treated as obstacles

        # Call the selected pathFinding algorithm
        if self.algo == "BFS":
            path, expanded = bfs(head, self.food, blocked)
        else:
            path, expanded = astar(head, self.food, blocked)

        self.nodes_expanded += expanded

        # If a valid path exists, follow the next step
        if path and len(path) > 1:
            next_cell = path[1]
            dx = next_cell[0] - head[0]
            dy = next_cell[1] - head[1]
            return dx, dy

        # No path → try any safe move
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = head[0] + dx, head[1] + dy
            if (0 <= nx < GRID_W and 0 <= ny < GRID_H and (nx, ny) not in blocked):
                return dx, dy

        # No safe move → keep current direction (death is likely)
        return self.direction

    def update(self):
        """Update snake position and handle collisions."""
        if not self.alive:
            return

        self.direction = self.choose_move()
        head = self.snake[0]
        dx, dy = self.direction
        nx, ny = head[0] + dx, head[1] + dy

        # Collision detection
        if not (0 <= nx < GRID_W and 0 <= ny < GRID_H) or (nx, ny) in self.snake:
            self.alive = False
            return

        # Move snake
        self.snake.insert(0, (nx, ny))

        if (nx, ny) == self.food:
            self.foods += 1
            self.spawn_food()
        else:
            self.snake.pop()

    def draw(self, screen):
        """Render grid, snake, and food."""
        bg_rect = pygame.Rect(self.offset_x, 0, BOARD_W, BOARD_H)
        pygame.draw.rect(screen, DARK2, bg_rect)

        # Draw grid lines
        for x in range(GRID_W):
            for y in range(GRID_H):
                rect = pygame.Rect(
                    self.offset_x + x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                pygame.draw.rect(screen, GRAY, rect, 1)

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(
                self.offset_x + x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            if i == 0:
                pygame.draw.rect(screen, YELLOW, rect, border_radius=4)  # Head
            else:
                pygame.draw.rect(screen, GREEN, rect, border_radius=4)   # Body

        # Draw food
        fx, fy = self.food
        rect = pygame.Rect(
            self.offset_x + fx * CELL_SIZE,
            fy * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )
        pygame.draw.rect(screen, RED, rect, border_radius=4)

        pygame.draw.rect(screen, BORDER, bg_rect, 3, border_radius=6)


# =============[ RACE GAME CLASS : تعرض النتائج وتدير واجهة المستخدم ]=================
class RaceGame:
    """
    Controls:
    - Both Snake boards (BFS vs A*)
    - Rendering
    - Statistics panel
    - Main game loop
    """
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake AI - BFS vs A*")

        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H)) #فتح نافذه اللعبه
        self.clock = pygame.time.Clock() #تحكم في سرعة اللعبة 

        self.font = pygame.font.SysFont("consolas", 20)
        self.title_font = pygame.font.SysFont("consolas", 26, bold=True)

        # Two side-by-side Snake boards
        self.bfs_board = SnakeBoard("BFS", 0)
        self.astar_board = SnakeBoard("ASTAR", BOARD_W)

    def draw_text_center(self, text, font, color, y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WINDOW_W // 2, y))
        self.screen.blit(surf, rect)

    def reset_game(self):
        """Reset both boards."""
        self.bfs_board.reset()
        self.astar_board.reset()

    def update(self):
        """Update both boards."""
        self.bfs_board.update()
        self.astar_board.update()

    def draw_labels_over_boards(self):
        bfs_label = self.title_font.render("BFS", True, PURPLE)
        self.screen.blit(bfs_label, bfs_label.get_rect(center=(BOARD_W // 2, 20)))

        ast_label = self.title_font.render("A*", True, BLUE)
        self.screen.blit(ast_label, ast_label.get_rect(center=(BOARD_W + BOARD_W // 2, 20)))

    def draw_panel(self):
        """Draw statistics and instructions panel."""
        panel_rect = pygame.Rect(0, BOARD_H, WINDOW_W, PANEL_H)
        pygame.draw.rect(self.screen, DARK2, panel_rect)

        bfs_f = self.bfs_board.foods
        ast_f = self.astar_board.foods

        bfs_nodes = self.bfs_board.nodes_expanded
        ast_nodes = self.astar_board.nodes_expanded

        # Stats output
        self.screen.blit(
            self.font.render(
                f"BFS - Foods: {bfs_f} | Nodes expanded: {bfs_nodes}",
                True,
                PURPLE,
            ),
            (20, BOARD_H + 20),
        )

        self.screen.blit(
            self.font.render(
                f"A*  - Foods: {ast_f} | Nodes expanded: {ast_nodes}",
                True,
                BLUE,
            ),
            (20, BOARD_H + 50),
        )

        # Controls
        info = "ESC: Quit   |   R: Restart"
        self.draw_text_center(info, self.font, WHITE, BOARD_H + PANEL_H - 30)

    def draw(self):
        """Render both boards and UI."""
        self.screen.fill(DARK)
        self.bfs_board.draw(self.screen)
        self.astar_board.draw(self.screen)
        self.draw_labels_over_boards()
        self.draw_panel()

    def run(self):
        """Main event loop."""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        self.reset_game()

            self.update()
            self.draw()

            pygame.display.update()
            self.clock.tick(FPS)


# ========= RUN GAME ==========
if __name__ == "__main__":
    RaceGame().run()
