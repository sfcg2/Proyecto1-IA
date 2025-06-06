import pygame
import sys
import random
import heapq
from collections import deque
import json
import time
import matplotlib.pyplot as plt

# === Configuración ===
TILE_SIZE = 150
ROWS, COLS = 4,4
EMPTY, OBSTACLE, START, GOAL = 0, 1, 2, 3
AGENTE_COLOR = 4
mensajes = [

    "Estado Inicial: (2,0)",
    " ",
    "Operadores: Arriba, Abajo, Izquierda, Derecha",
    " ",
    "Costo de cada celda: 1",
    " ",
    "Meta: El ratón encuentra el queso.",
    " ",
    "*Evita devolverse"
]
# Colores
COLORS = {
    0: (255, 255, 255),        # blanco (vacío)
    1: (183, 194, 194),           # gris oscuro (obstáculo)
    2: (102, 248, 12),            # verde (inicio)
    3: (243, 183, 22),            # amarillo (objetivo)
    4: (161, 161, 161),           # color del raton 
    'visited': (100, 149, 237),   # azul claro (explorado)
    'path': (255, 255, 0)         # amarillo (camino)
}

# Variables globales
start = (0, 0)       # Posición inicial por defecto
goal = (ROWS - 1, COLS - 1)  # Posición objetivo por defecto
maze = []

# --- Funciones auxiliares ---
def get_neighbors(pos):
    x, y = pos
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < ROWS and 0 <= ny < COLS and maze[nx][ny] != 1:
            yield (nx, ny)

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, start, goal):
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return []
    path.reverse()
    return path

# --- Búsquedas ---
def bfs(start, goal, screen):
    queue = deque([start])
    came_from = {start: None}

    while queue:
        pygame.time.delay(50)  # pausa para animar
        current = queue.popleft()

        if current == goal:
            break

        for neighbor in get_neighbors(current):
            if neighbor not in came_from:
                queue.append(neighbor)
                came_from[neighbor] = current

                # marcar explorado
                if maze[neighbor[0]][neighbor[1]] not in [2, 3]:
                    draw_tile(screen, neighbor, 'visited')
        pygame.display.flip()

    return reconstruct_path(came_from, start, goal)

def dfs(start, goal, screen):
    stack = [start]
    came_from = {start: None}

    while stack:
        pygame.time.delay(50)  # pausa para animar
        current = stack.pop()

        if current == goal:
            break

        for neighbor in get_neighbors(current):
            if neighbor not in came_from:
                stack.append(neighbor)
                came_from[neighbor] = current

                # marcar explorado
                if maze[neighbor[0]][neighbor[1]] not in [2, 3]:
                    draw_tile(screen, neighbor, 'visited')
        pygame.display.flip()

    return reconstruct_path(came_from, start, goal)

def a_star(start, goal, screen):
    frontier = []
    mensajes.clear()
    draw_sidebar(screen)
    iteraciones = 0
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        pygame.time.delay(50)  # pausa para animar
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for neighbor in get_neighbors(current):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heuristica = manhattan(neighbor, goal)
                priority = new_cost + heuristica
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

                # marcar explorado
                if maze[neighbor[0]][neighbor[1]] not in [2, 3]:
                    draw_tile(screen, neighbor, 'visited')
        pygame.display.flip()
    mensajes.append(f'f({iteraciones+1}): {new_cost} + {heuristica} = {priority}')
    iteraciones += 1

    return reconstruct_path(came_from, start, goal)

#Dibuja el laberinto
def draw_tile(screen, pos, cell_type):
    color = COLORS[cell_type] if isinstance(cell_type, int) else COLORS[cell_type]
    pygame.draw.rect(screen, color, (pos[1] * TILE_SIZE, pos[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, (79, 93, 98), (pos[1] * TILE_SIZE, pos[0] * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

def draw_maze(screen, path=None, agente_pos=None):
    for i in range(ROWS):
        for j in range(COLS):
            draw_tile(screen, (i, j), maze[i][j])
    if path:
        for pos in path:
            if maze[pos[0]][pos[1]] not in [2, 3]:
                draw_tile(screen, pos, 'path')
    if agente_pos:
        # dibujar agente como círculo
        x, y = agente_pos
        center = (y * TILE_SIZE + TILE_SIZE // 2, x * TILE_SIZE + TILE_SIZE // 2)
        radius = TILE_SIZE // 3
        pygame.draw.circle(screen, AGENTE_COLOR, center, radius)
    pygame.display.flip()

# --- Animación del agente ---
def animate_agente(screen, path):
    agente_pos = path[0]
    for pos in path[1:]:
        agente_pos = pos
        draw_maze(screen, path, agente_pos)
        pygame.time.delay(200)
    return agente_pos

# --- Cargar configuración desde archivo JSON ---
def load_maze_from_file(filename):
    global ROWS, COLS, start, goal, maze
    try:
        with open(filename, 'r') as file:
            config = json.load(file)
        
        ROWS, COLS = config['rows'], config['cols']
        start = tuple(config['start'])
        goal = tuple(config['goal'])
        
        # Inicializar el laberinto
        maze = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        maze[start[0]][start[1]] = 2  # START
        maze[goal[0]][goal[1]] = 3    # GOAL
        
        # Agregar obstáculos
        for obstacle in config.get('obstacles', []):
            row, col = obstacle
            maze[row][col] = 1  # OBSTACLE
    except Exception as e:
        almacenamiento_mensajes(f"Error al cargar el archivo de configuración: {e}")
        sys.exit()

# --- Búsqueda por Costo Uniforme ---
def uniform_cost_search(start, goal, screen):
    frontier = []
    mensajes.clear()
    draw_sidebar(screen)
    heapq.heappush(frontier, (0, start))  # (costo, posición)
    came_from = {start: None}
    cost_so_far = {start: 0}
    iteraciones = 0
    
    while frontier:
        pygame.time.delay(50)  # pausa para animar
        current_cost, current = heapq.heappop(frontier)

        if current == goal:
            break

        for neighbor in get_neighbors(current):
            new_cost = cost_so_far[current] + 1  # costo uniforme: cada paso tiene costo 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost  # Prioridad es solo el costo acumulado
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current
                # marcar explorado
                if maze[neighbor[0]][neighbor[1]] not in [2, 3]:
                    draw_tile(screen, neighbor, 'visited')
        pygame.display.flip()
        mensajes.append(f'El costo total g({iteraciones+1}): {new_cost}')
        iteraciones += 1
    return reconstruct_path(came_from, start, goal)


# --- Búsqueda Avara ---
def greedy_best_first_search(start, goal, screen):
    frontier = []
    mensajes.clear()
    draw_sidebar(screen)
    iteraciones = 0
    heapq.heappush(frontier, (manhattan(start, goal), start))  # (heurística, posición)
    came_from = {start: None}

    while frontier:
        pygame.time.delay(50)  # pausa para animar
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for neighbor in get_neighbors(current):
            if neighbor not in came_from:
                priority = manhattan(neighbor, goal)  # Solo usa la heurística
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current
                # marcar explorado
                if maze[neighbor[0]][neighbor[1]] not in [2, 3]:
                    draw_tile(screen, neighbor, 'visited')
        pygame.display.flip()
        mensajes.append(f'H({iteraciones+1}): {priority}')
        iteraciones += 1

    return reconstruct_path(came_from, start, goal)


# --- Búsqueda Híbrida Actualizada ---
def hybrid_search(start, goal, screen):
    mensajes.clear()
    draw_sidebar(screen)
    almacenamiento_mensajes("Intentando BFS...")
    path = bfs(start, goal, screen)
    if path:
        almacenamiento_mensajes("Ruta encontrada con BFS.")
        return path

    almacenamiento_mensajes("- BFS falló. Intentando A*...")
    path = a_star(start, goal, screen)
    if path:
        almacenamiento_mensajes("- Ruta encontrada con A*.")
        return path

    almacenamiento_mensajes("- A* falló. Intentando Búsqueda por Costo Uniforme...")
    path = uniform_cost_search(start, goal, screen)
    if path:
        almacenamiento_mensajes(":) Ruta encontrada con Búsqueda por Costo Uniforme.")
        return path

    almacenamiento_mensajes("- Costo Uniforme falló. Intentando Búsqueda Avara...")
    path = greedy_best_first_search(start, goal, screen)
    if path:
        almacenamiento_mensajes(":) Ruta encontrada con Búsqueda Avara.")
        return path

    almacenamiento_mensajes("- Búsqueda Avara falló. Intentando DFS...")
    path = dfs(start, goal, screen)
    if path:
        almacenamiento_mensajes(":) Ruta encontrada con DFS.")
        return path

    almacenamiento_mensajes(":( No se encontró una ruta válida con ninguna técnica.")
    return None


def almacenamiento_mensajes(mensaje):
    mensajes.append(mensaje)

# --- Actualización del Sidebar ---
def draw_sidebar(screen):
    sidebar_width = 400
    pygame.draw.rect(screen, (192, 227, 237), (COLS * TILE_SIZE, 0, sidebar_width, ROWS * TILE_SIZE + 20))
    font = pygame.font.SysFont("Comic Sans", 17)
    instructions = [
        "1: BFS",
        "2: DFS",
        "3: A*",
        "4: Costo Uniforme",
        "5: Búsqueda Avara",
        "H: Búsqueda Híbrida",
        "R: Reiniciar",
        "M: Mover Meta",
        "S: Establecer Inicio",
        "G: Establecer Objetivo",
        "T: Tiempos de Ejecución"
        "Click: Agregar/Quitar Obstáculo"
    ]
    for i, text in enumerate(instructions):
        img = font.render(text, True, (0, 0, 0))
        screen.blit(img, (COLS * TILE_SIZE + 10, 10 + i * 35))

    #Area donde muestra los mensajes, cuando cambia de un algoritmo a otro
    area_x = COLS * TILE_SIZE + 10
    area_y = 400
    area_ancho = sidebar_width - 20
    area_altura = 200
    
    pygame.draw.rect(screen, (255, 255, 255), (area_x, area_y, area_ancho, area_altura),0,20)
    font = pygame.font.SysFont("Comic Sans", 17)

    for i, mensj in enumerate(mensajes):
        img = font.render(mensj, True, (0, 0, 0))
        screen.blit(img, (area_x + 5, area_y+5 + i *20))
    
def main():
    pygame.init()
    global ROWS, COLS, start, goal, maze
    # Cargar configuración inicial
    load_maze_from_file("maze_config.json")
    screen = pygame.display.set_mode((COLS * TILE_SIZE + 400, ROWS * TILE_SIZE+10))
    pygame.display.set_caption("Agente Inteligente - Laberinto Dinámico")
    running = True
    path = []
    agente_pos = start
    
    #Datos grafica
    nombres_algt = []
    tiempos = []

    while running:
        draw_maze(screen, path, agente_pos)
        draw_sidebar(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif pygame.mouse.get_pressed()[0]:  # Click izquierdo
                x, y = pygame.mouse.get_pos()
                row, col = y // TILE_SIZE, x // TILE_SIZE
                if (row, col) not in [start, goal]:
                    maze[row][col] = 1 if maze[row][col] == 0 else 0
            elif event.type == pygame.KEYDOWN:

                def mide_tiempo(algoritmo, nombre):
                    
                    inicio = time.time()
                    path = algoritmo(start, goal, screen)
                    tiempo = time.time() - inicio
                    nombres_algt.append(nombre)
                    tiempos.append(tiempo)
                    if path:
                        animate_agente(screen, path)
                    else:
                        almacenamiento_mensajes(f"No se encontró una ruta válida con {nombre}.")

                if event.key == pygame.K_1:  # BFS
                    mensajes.clear()
                    draw_sidebar(screen)
                    path = bfs(start, goal, screen)
                    mide_tiempo(bfs,"BFS")
                    if path:
                        agente_pos = animate_agente(screen, path)
                    else:
                        almacenamiento_mensajes("No se encontró una ruta válida con BFS.")
                elif event.key == pygame.K_2:  # DFS
                    draw_sidebar(screen)
                    mide_tiempo(dfs,"DFS")
                    path = dfs(start, goal, screen)
                    if path:
                        agente_pos = animate_agente(screen, path)
                    else:
                        almacenamiento_mensajes("No se encontró una ruta válida con DFS.")
                elif event.key == pygame.K_3:  # A*
                    draw_sidebar(screen)
                    mide_tiempo(dfs,"A*")
                    path = a_star(start, goal, screen)
                    if path:
                        agente_pos = animate_agente(screen, path)
                    else:
                        almacenamiento_mensajes("No se encontró una ruta válida con A*.")
                elif event.key == pygame.K_4:  # Costo Uniforme
                    draw_sidebar(screen)
                    mide_tiempo(dfs,"Costo Uniforme")
                    path = uniform_cost_search(start, goal, screen)
                    if path:
                        agente_pos = animate_agente(screen, path)
                    else:
                        almacenamiento_mensajes("No se encontró una ruta válida con Costo Uniforme.")
                elif event.key == pygame.K_5:  # Búsqueda Avara
                    draw_sidebar(screen)
                    mide_tiempo(dfs,"Búsqueda Avara")
                    path = greedy_best_first_search(start, goal, screen)
                    if path:
                        agente_pos = animate_agente(screen, path)
                    else:
                        almacenamiento_mensajes("No se encontró una ruta válida con Búsqueda Avara.")
                elif event.key == pygame.K_h:  # Búsqueda híbrida
                    draw_sidebar(screen)
                    mide_tiempo(dfs,"Busqueda Hibrida")
                    path = hybrid_search(start, goal, screen)
                    if path:
                        agente_pos = animate_agente(screen, path)
                    else:
                        almacenamiento_mensajes("No se encontró una ruta válida con la búsqueda híbrida.")
                elif event.key == pygame.K_r:  # Reiniciar
                    nombres_algt.clear()
                    tiempos.clear()
                    mensajes.clear()
                    load_maze_from_file("maze_config.json")
                    path = []
                    agente_pos = start
                elif event.key == pygame.K_m:  # Mover meta
                    nombres_algt.clear()
                    tiempos.clear()
                    mensajes.clear()
                    maze[goal[0]][goal[1]] = 0  # Limpiar la antigua posición
                    new_goal = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
                    goal = new_goal
                    maze[goal[0]][goal[1]] = 3  # Establecer nueva posición
                elif event.key == pygame.K_s:  # Establecer nueva posición de inicio
                    nombres_algt.clear()
                    tiempos.clear()
                    mensajes.clear()
                    x, y = pygame.mouse.get_pos()
                    row, col = y // TILE_SIZE, x // TILE_SIZE
                    if (row, col) != goal:
                        maze[start[0]][start[1]] = 0  # Limpiar la antigua posición
                        start = (row, col)
                        maze[start[0]][start[1]] = 2  # Establecer nueva posición
                        agente_pos = start
                elif event.key == pygame.K_g:  # Establecer nueva posición de objetivo
                    nombres_algt.clear()
                    tiempos.clear()
                    mensajes.clear()
                    x, y = pygame.mouse.get_pos()
                    row, col = y // TILE_SIZE, x // TILE_SIZE
                    if (row, col) != start:
                        maze[goal[0]][goal[1]] = 0  # Limpiar la antigua posición
                        goal = (row, col)
                        maze[goal[0]][goal[1]] = 3  # Establecer nueva posición
                
                elif event.key == pygame.K_t:
                    print(nombres_algt)
                    print(tiempos)
                    print(mensajes)
                    if nombres_algt and tiempos:
                        draw_sidebar(screen)
                        plt.figure(figsize=(10, 6))
                        barras = plt.bar(nombres_algt, tiempos, color='skyblue')
                        for i, bar in enumerate(barras):
                            height = bar.get_height()  # Altura de la barra
                            plt.text(
                                bar.get_x() + bar.get_width() / 2,  # Posición horizontal (centro de la barra)
                                height + 0.02,                      # Posición vertical (ligeramente encima de la barra)
                                f"{tiempos[i]:.4f}",                # Texto: tiempo con 4 decimales
                                ha='center',                        # Alineación horizontal centrada
                                fontsize=10                         # Tamaño de fuente
        )
                        plt.xlabel("Algoritmos")
                        plt.ylabel("Tiempo (segundos)")
                        plt.title("Comparación de Tiempos de Ejecución")
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        plt.show()
                    else:   
                        print("nada que mostrar")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()