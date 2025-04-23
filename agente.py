import pygame # type: ignore
import sys
import heapq
import time

TILE_SIZE = 40
ROWS, COLS = 10, 15
EMPTY, OBSTACLE, START, GOAL = 0, 1, 2, 3

# Colores
COLORS = {
    EMPTY: (255, 255, 255),
    OBSTACLE: (50, 50, 50),
    START: (0, 200, 0),
    GOAL: (200, 0, 0),
    'visited': (100, 149, 237),
    'path': (255, 255, 0)
}

# Iniciar laberinto vacío
maze = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
start = (0, 0)
goal = (ROWS - 1, COLS - 1)
maze[start[0]][start[1]] = START
maze[goal[0]][goal[1]] = GOAL


def get_neighbors(pos):
    x, y = pos
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < ROWS and 0 <= ny < COLS:
            if maze[nx][ny] != OBSTACLE:
                yield (nx, ny)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(screen, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        pygame.time.delay(50)
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for neighbor in get_neighbors(current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + manhattan(neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

                if maze[neighbor[0]][neighbor[1]] not in [START, GOAL]:
                    draw_tile(screen, neighbor, 'visited')
        pygame.display.flip()

    return reconstruct_path(came_from, start, goal)


def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return []  # No path
    path.reverse()
    return path


def draw_tile(screen, pos, type):
    color = COLORS[type] if isinstance(type, str) else COLORS.get(type, (100, 100, 100))
    pygame.draw.rect(screen, color, (pos[1]*TILE_SIZE, pos[0]*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, (180, 180, 180), (pos[1]*TILE_SIZE, pos[0]*TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)


def draw_maze(screen, path=None):
    for i in range(ROWS):
        for j in range(COLS):
            draw_tile(screen, (i, j), maze[i][j])
    if path:
        for pos in path:
            if maze[pos[0]][pos[1]] not in [START, GOAL]:
                draw_tile(screen, pos, 'path')
    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((COLS*TILE_SIZE, ROWS*TILE_SIZE))
    pygame.display.set_caption("Agente Inteligente - Laberinto Dinámico")
    running = True
    placing = OBSTACLE
    path = []

    while running:
        draw_maze(screen, path)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif pygame.mouse.get_pressed()[0]:  # Click izquierdo
                x, y = pygame.mouse.get_pos()
                row, col = y // TILE_SIZE, x // TILE_SIZE
                if (row, col) not in [start, goal]:
                    maze[row][col] = OBSTACLE if maze[row][col] == EMPTY else EMPTY

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    path = a_star(screen, start, goal)
                elif event.key == pygame.K_r:
                    for i in range(ROWS):
                        for j in range(COLS):
                            if maze[i][j] not in [START, GOAL]:
                                maze[i][j] = EMPTY
                    path = []

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
