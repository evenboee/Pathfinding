"""
Base matrix
0  0  0  0  0  0  0
0  1  1  1  1  1  0
0  1  1  1  1  1  0
0  1  1  1  1  1  0
0  1  1  1  1  1  0
0  1  1  1  1  1  0
0  0  0  0  0  0  0

Numbered matrix (note: 0 in position [1, 1] is not a wall, just the number 0)
0  0  0  0  0  0  0
0  0  1  2  3  4  0
0  5  6  7  8  9  0
0 10 11 12 13 14  0
0 15 16 17 18 19  0
0 20 21 22 23 24  0
0  0  0  0  0  0  0
"""

import pygame
import time as timez

w = 30
h = 30
wall = 0  # Defining what number to associate with a wall in the matrix
start = 50  # Number of the start node
target = 19  # Number of the target node


# Returns the x and y coordinates of the node with number num
def num_to_array(num):
    return [(num % w) + 1, (num // w) + 1]


target_xy = num_to_array(target)
start_xy = num_to_array(start)


# Estimate the distance left to the target node from node number n (using manhattan distance)
def get_h_cost(n):
    tt = num_to_array(n)
    dx = abs(target_xy[0] - tt[0])
    dy = abs(target_xy[1] - tt[1])
    d = dx + dy
    return d


# Filling matrix with values
matrix = []
filler = [wall for i in range(w + 2)]
matrix.append(filler)
for i in range(h):
    arr = [1 for _ in range(w + 2)]
    arr[0] = arr[len(arr) - 1] = wall
    matrix.append(arr)
matrix.append(filler)

# Creating walls
walls = []  # [5, 15, 25, 35, 45, 55, 65, 75, 85]
for wl in walls:
    wall_pos = num_to_array(wl)
    print(f'Creating wall at: {wall_pos}')
    matrix[wall_pos[1]][wall_pos[0]] = wall


scl = int(900 / h)
pygame.init()

# Create screen
screen = pygame.display.set_mode((w * scl, h * scl))
pygame.display.set_caption('A*')
clock = pygame.time.Clock()


class Path:
    def __init__(self):
        self.tbe = {start: [0, 0, -1, start]}  # TBE = To Be Evaluated. Entry: [fCost, gCost, parent, self]
        self.fin = {}  # Fin = Finished / Done
        self.found = False
        if matrix[target_xy[1]][target_xy[0]] == wall:
            matrix[target_xy[1]][target_xy[0]] = 1
        self.solution = []


    def finished(self):
        return len(self.tbe) == 0 or self.found

    def get_f_value_of_node(self, n):
        return n[0]

    def step(self):
        if not self.found:
            # Finding the key with the lowest f_cost
            lowest = [-1, 1000000]  # The currently lowest key
            for i in self.tbe:  # Checking all keys
                if self.tbe[i][0] < lowest[1]:  # If this keys value is less than the currently lowest: change it
                    lowest = [i, self.tbe.get(i)[0]]
            current = lowest[0]  # Current node under evaluation is the one with the lowest f_cost in the list
            current_values = self.tbe[current]
            self.fin[current] = self.tbe[current]  # Adding node to finished list

            self.tbe.pop(current)  # Removing node from To Be Evaluated list

            if current == target:  # If the node is the target node: Finish
                self.found = True
                return

            current_pos = num_to_array(current)  # Matrix position of the node currently under evaluation
            # [number, [dx, dy]]. Alt. if diagonals [number, [dx, dy], weight]
            possible_neighbours = [[current - w, [0, -1]], [current + w, [0, 1]], [current + 1, [1, 0]],
                                   [current - 1, [-1, 0]]]
            for nb in possible_neighbours:
                n = nb[0]  # Number of the neighbour node
                nxy = [current_pos[0] + nb[1][0], current_pos[1] + nb[1][1]]  # x and y positions of the neighbour node
                if matrix[nxy[1]][nxy[0]] == wall or n in self.fin:  # If the neighbour is a wall or has been evaluated:
                    continue  # Skip to the next neighbour

                n_g_cost = current_values[1] + 1  # The g_cost of the neighbour. Distance traveled so far
                n_h_cost = get_h_cost(n)  # The h_cost of the neighbour. Estimate of distance left
                n_f_cost = n_g_cost + n_h_cost  # Estimate of the total length to the node
                if n in self.tbe:  # If the node is already in the To Be Estimated queue (it already has a path to it):
                    if self.tbe[n][0] > n_f_cost:  # And the estimated weight is lower:
                        self.tbe[n] = [n_f_cost, n_g_cost, current, n]  # Change the value
                else:  # If it is not in the To Be Estimated queue:
                    self.tbe[n] = [n_f_cost, n_g_cost, current, n]  # Add it


    def finish(self):
        self.solution = []
        keys = list(self.fin.keys())
        goal = self.fin[keys[len(keys) - 1]]
        if goal[3] != target:  # If the first is not the target then the path was not found
            print('Did not find path')
            return None
        else:
            while True:  # Traversing parents from target node to start node
                goal = self.fin.get(goal[2])  # Next node is the parent of the current node
                if goal[2] == -1:
                    break
                self.solution.append(goal[3])  # Adding current node to the solution

        self.solution = list(reversed(self.solution))
        return self.solution


    def draw_step(self, surface):
        for n in self.tbe.keys():
            coor = num_to_array(self.tbe[n][3])
            pygame.draw.rect(surface, (173, 216, 230), ((coor[0] - 1) * scl + 1, (coor[1] - 1) * scl + 1, scl - 1, scl - 1))
        for n in self.fin:
            coor = num_to_array(self.fin[n][3])
            pygame.draw.rect(surface, (128, 0, 128), ((coor[0] - 1) * scl + 1, (coor[1] - 1) * scl + 1, scl - 1, scl - 1))


    def draw_solution(self, surface, slow=False):
        for n in self.solution:
            nxy = num_to_array(n)
            pygame.draw.rect(surface, (0, 0, 200), ((nxy[0] - 1) * scl + 1, (nxy[1] - 1) * scl + 1, scl - 1, scl - 1))
            if slow:
                pygame.display.update()
                timez.sleep(0.05)


def draw_background(surface):
    surface.fill((55, 55, 55))


def draw_lines(surface):
    if scl > 15:
        for i in range(1, w):  # Drawing vertical lines
            pygame.draw.line(surface, (220, 220, 220), (i * scl, 0), (i * scl, h * scl), 1)
        for i in range(1, h):  # Drawing horizontal lines
            pygame.draw.line(surface, (220, 220, 220), (0, i * scl), (w * scl, i * scl), 1)


def draw_walls(surface):
    for y in range(len(matrix) - 2):
        for x in range(len(matrix[y]) - 2):
            if matrix[y + 1][x + 1] == wall:
                pygame.draw.rect(surface, (255, 0, 0), (scl * x + 1, scl * y + 1, scl - 1, scl - 1))


def draw_start_end_nodes(surface):
    # Start Node
    pygame.draw.rect(surface, (0, 0, 255), ((start_xy[0] - 1) * scl + 1, (start_xy[1] - 1) * scl + 1, scl - 1, scl - 1))
    # Target node
    pygame.draw.rect(surface, (0, 255, 0), ((target_xy[0] - 1) * scl + 1, (target_xy[1] - 1) * scl + 1, scl - 1, scl - 1))


def draw_all(surface, path=None):
    draw_background(surface)
    draw_lines(surface)

    if path is not None:
        path.draw_step(screen)

    draw_walls(surface)

    if path is not None:
        draw_start_end_nodes(surface)

    pygame.display.update()


def main():
    global target_xy, start_xy, target, start
    step_rate = 50
    solver = Path()
    visualize = False
    running = True
    l_mouse_down = False
    r_mouse_down = False
    ctrl_button_down = False
    brush_size = 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    solver = Path()
                    visualize = True
                elif event.key == pygame.K_n:
                    solver = Path()
                elif event.key == pygame.K_1:
                    brush_size = 1
                elif event.key == pygame.K_3:
                    brush_size = 3
                elif event.key == pygame.K_LCTRL:
                    ctrl_button_down = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL:
                    ctrl_button_down = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] == 1:
                    l_mouse_down = True
                if pygame.mouse.get_pressed()[2] == 1:
                    r_mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if pygame.mouse.get_pressed()[0] == 0:
                    l_mouse_down = False
                if pygame.mouse.get_pressed()[2] == 0:
                    r_mouse_down = False
        mouse_pos = pygame.mouse.get_pos()
        mouse_square_pos = [(mouse_pos[0] // scl) + 1, (mouse_pos[1] // scl) + 1]  # The matrix position of the mouse

        if target_xy != mouse_square_pos:
            if ctrl_button_down and l_mouse_down:
                solver = Path()
                if matrix[mouse_square_pos[1]][mouse_square_pos[0]] != wall:
                    start = mouse_square_pos[0] - 1 + (mouse_square_pos[1] - 1) * w
                    start_xy = num_to_array(start)
            elif ctrl_button_down and r_mouse_down:  # matrix[mouse_square_pos[1]][mouse_square_pos[0]] != wall
                solver = Path()
                if matrix[mouse_square_pos[1]][mouse_square_pos[0]] != wall:
                    target = mouse_square_pos[0] - 1 + (mouse_square_pos[1] - 1) * w
                    target_xy = num_to_array(target)
            elif l_mouse_down or r_mouse_down:
                solver = Path()
                value_set = 1 if r_mouse_down else wall
                others = [[0, 0]]
                if brush_size == 3:
                    others = [[0, 0], [-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
                for direction in others:
                    dirPos = [mouse_square_pos[0] + direction[0], mouse_square_pos[1] + direction[1]]
                    if dirPos == target_xy:
                        continue
                    if len(matrix) - 1 > dirPos[1] > 0 and len(matrix[0]) - 1 > dirPos[0] > 0:
                        matrix[mouse_square_pos[1] + direction[1]][mouse_square_pos[0] + direction[0]] = value_set

        draw_background(screen)
        draw_lines(screen)
        draw_walls(screen)

        if visualize:
            while not solver.finished():
                dt = clock.tick(step_rate)
                solver.step()
                draw_all(screen, solver)
            solver.finish()
            visualize = False
            solver.draw_solution(screen, True)

        if solver.finished():
            solver.draw_step(screen)
            solver.draw_solution(screen)

        draw_walls(screen)

        # Start Node
        pygame.draw.rect(screen, (0, 0, 255),
                         ((start_xy[0] - 1) * scl + 1, (start_xy[1] - 1) * scl + 1, scl - 1, scl - 1))
        # Target node
        pygame.draw.rect(screen, (0, 255, 0),
                         ((target_xy[0] - 1) * scl + 1, (target_xy[1] - 1) * scl + 1, scl - 1, scl - 1))

        pygame.display.update()


main()
