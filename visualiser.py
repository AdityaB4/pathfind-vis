# Array like indexing in grid and regular x,y indexing for pygame methods

# reset grid check value and reference pass for start and end state reset to None

import pygame
import math
from queue import PriorityQueue

LEN = 800
WIN = pygame.display.set_mode((LEN, LEN))
pygame.display.set_caption("A* Visualiser")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (100, 100, 255)
DARKBLUE = (10, 10, 120)


class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.colour = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_checked(self):
        return self.colour == RED

    def is_barrier(self):
        return self.colour == BLACK

    def is_open(self):
        return self.colour == GREEN

    def is_start(self):
        return self.colour == YELLOW

    def is_end(self):
        return self.colour == PURPLE

    def is_blank(self):
        return self.colour == WHITE

    def reset(self):
        self.colour = WHITE

    def make_checked(self):
        self.colour = RED

    def make_barrier(self):
        self.colour = BLACK

    def make_open(self):
        self.colour = GREEN

    def make_start(self):
        self.colour = YELLOW

    def make_end(self):
        self.colour = PURPLE

    def make_path(self):
        self.colour = DARKBLUE

    def draw(self, win):
        pygame.draw.rect(win, self.colour,
                         (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        
        # self.neighbours = [] # reset each run but why

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbours.append(grid[self.row - 1][self.col])
        
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbours.append(grid[self.row][self.col - 1])
        
    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1-x2) + abs(y1-y2)

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, BLACK, (0, i * gap), (width, i * gap))

        for j in range(rows):
            pygame.draw.line(win, BLACK, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_click_pos(pos, rows, width):
    gap = width // rows
    i, j = pos

    row = i // gap
    col = j // gap

    return row, col


def algorithm(draw, grid, start, end):
    count = 0 # to check for ties
    open_set = PriorityQueue()
    open_set.put((0, count, start)) # (f, order, node)
    prev = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        curr = (open_set.get())[2]
        open_set_hash.remove(curr)

        if curr == end:
            end.make_end() # to reset to end colour after green overwrite
            
            # re-trace path
            curr_path_node = prev[curr] # so that end is not coloured as path
            while prev:
                if curr_path_node == start:
                    break #stop here (better to just change while to while curr in prev or something like that)
                curr_path_node.make_path()
                prev_path_node = prev[curr_path_node]
                prev.pop(curr_path_node)
                curr_path_node = prev_path_node
                draw() #YYYYYYY
            
            return True

        for neighbour in curr.neighbours:
            temp_g_score = g_score[curr] + 1

            if temp_g_score < g_score[neighbour]:
                prev[neighbour] = curr
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = g_score[neighbour] + h(neighbour.get_pos(), end.get_pos())

                if neighbour not in open_set_hash:
                    open_set_hash.add(neighbour)
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    neighbour.make_open()

        draw() #YYYYYY

        if curr != start:
            curr.make_checked()

        
    return False





def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                node = grid[row][col]
                if node.is_blank():
                    if not start:
                        start = node
                        start.make_start()

                    elif not end:
                        end = node
                        end.make_end()

                    elif node != (end or start):
                        node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                node = grid[row][col]
                if node.is_start():
                    start = None
                elif node.is_end():
                    end = None
                node.reset()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid) # Bcz you want a list of everyone's neighbours

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                elif event.key == pygame.K_ESCAPE:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, LEN)