import pygame
import sys
from config import COLORS, GRID_SIZE, CELL_SIZE
from collections import deque


def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    window.blit(text_surface, text_rect)


def draw_board():
    for i in range(0, GRID_SIZE+1):
        pygame.draw.line(window, 
                         COLORS['TEXT_PURPLE'], 
                         (100+i*CELL_SIZE,CELL_SIZE), 
                         (100+i*CELL_SIZE, 100+CELL_SIZE*GRID_SIZE), 3)
        pygame.draw.line(window, 
                         COLORS['TEXT_PURPLE'], 
                         (CELL_SIZE, 100+i*CELL_SIZE), 
                         (100+GRID_SIZE*CELL_SIZE, 100+CELL_SIZE*i), 
                         3)
    status_text = [f'{player.capitalize()}: Select a Pawn or Fence', 
                   f'{player.capitalize()}: Select a destination', 
                   f'{player.capitalize()}: Select a place']
    
    text_back = FONTS['MAIN_FONT'].render("Back", True, COLORS['TEXT_PURPLE'])
    button_back = text_back.get_rect(center=(window_width-200, 100))
    pygame.draw.rect(window, COLORS['LIGHT_PURPLE'], button_back.inflate(20, 20))
    window.blit(text_back, button_back)

    window.blit(FONTS['MAIN_FONT'].render(status_text[turn_step], True, COLORS['WHITE']), (1100, 200))
    window.blit(FONTS['MAIN_FONT'].render(f'Red walls: {red_walls}', True, COLORS['WHITE']), (1100, 600))
    window.blit(FONTS['MAIN_FONT'].render(f'Yellow walls: {yellow_walls}', True, COLORS['WHITE']), (1100, 800))

    pygame.draw.rect(window, COLORS['TEXT_PURPLE'], (1100, 700, 200,10))
    pygame.draw.rect(window, COLORS['TEXT_PURPLE'], (1500, 700, 10,200))


def draw_players():
    pygame.draw.circle(window, 
                       COLORS['RED'], 
                       (red_pos[1]*CELL_SIZE+100+CELL_SIZE/2, red_pos[0]*CELL_SIZE+100+CELL_SIZE/2), 
                       20)
    pygame.draw.circle(window, COLORS['YELLOW'], (yellow_pos[1]*CELL_SIZE+100+CELL_SIZE/2, yellow_pos[0]*CELL_SIZE+100+CELL_SIZE/2), 20)


def get_valid_moves(pos):
    def no_pawn(p):
        return p != red_pos and p != yellow_pos

    def no_wall(walls_dir, walls):
        return all(wall not in walls for wall in walls_dir)

    x, y = pos
    valid_moves = []
    directions = {
        'top': (0, -1),
        'bottom': (0, 1),
        'left': (-1, 0),
        'right': (1, 0)
    }

    for direction, (dx, dy) in directions.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            walls = {
                'top': [(y + CELL_SIZE, x + CELL_SIZE), (y, x + CELL_SIZE)],
                'bottom': [(y + 2 * CELL_SIZE, x + 2 * CELL_SIZE), (y, x + 2 * CELL_SIZE)],
                'left': [(y + CELL_SIZE, x), (y + CELL_SIZE, x + CELL_SIZE)],
                'right': [(y + CELL_SIZE, x + 2 * CELL_SIZE), (y + CELL_SIZE, x)]
            }
            if no_pawn((nx, ny)) and no_wall(walls[direction], horizontal_walls if direction in ('top', 'bottom') else vertical_walls):
                valid_moves.append((nx, ny))
            elif 0 <= nx + dx < GRID_SIZE and 0 <= ny + dy < GRID_SIZE and not no_pawn((nx, ny)):
                valid_moves.append((nx + dx, ny + dy))

    return valid_moves


def delete_ways(possible_ways, horizontal_walls, vertical_walls):
    possible_lines = set(possible_ways)

    horizontal_delta = [[50, -50, 50, 50], [150, -50, 150, 50]]
    vertical_delta = [[-50, 50, 50, 50], [-50, 150, 50, 150]]

    for hx, hy in horizontal_walls:
        for delta in horizontal_delta:
            line = ((hx + delta[0], hy + delta[1]), (hx + delta[2], hy + delta[3]))
            if line in possible_lines:
                possible_lines.remove(line)

    for vx, vy in vertical_walls:
        for delta in vertical_delta:
            line = ((vx + delta[0], vy + delta[1]), (vx + delta[2], vy + delta[3]))
            if line in possible_lines:
                possible_lines.remove(line)

    return list(possible_lines)


def is_winnable(player_x, player_y, horizontal_lines, vertical_lines, target):
    new_possible_lines = delete_ways(possible_ways, horizontal_lines, vertical_lines)

    def get_neighbors(square):
        (x, y) = square
        return {(x + 100, y), (x - 100, y), (x, y + 100), (x, y - 100)}
    

    start = (player_x, player_y)
    queue = deque([start])
    paths = {start: [start]}
    while queue:
        s = queue.popleft()
        if s[1] == target:
            return paths[s]
        for s2 in get_neighbors(s):
            if s2 not in paths and tuple(sorted([s, s2])) in new_possible_lines:
                queue.append(s2)
                paths[s2] = paths.get(s, []) + [s2]
    return None


def game_turn(click_coords):
    global valid_pawn_moves, red_pos, yellow_pos, player, turn_step, red_walls, yellow_walls, wall, game
    if not game:
        return 0
    if player == 'red':
        pawn_pos, walls_left, opponent = red_pos, red_walls, 'yellow'
    else:
        pawn_pos, walls_left, opponent = yellow_pos, yellow_walls, 'red'

    pawn_coords = (pawn_pos[1] + 1, pawn_pos[0] + 1)
    click_rcords = (click_coords[1] - 1, click_coords[0] - 1)

    if click_coords == pawn_coords and not valid_pawn_moves:
        valid_pawn_moves = get_valid_moves(pawn_pos)
        turn_step = 1
    elif valid_pawn_moves and click_rcords in valid_pawn_moves:
        if player == 'red':
            red_pos = click_rcords
        else:
            yellow_pos = click_rcords

        valid_pawn_moves = []
        player = opponent
        turn_step = 0
    elif valid_pawn_moves and click_rcords not in valid_pawn_moves:
        valid_pawn_moves = []
        turn_step = 0
    elif turn_step == 0 and 1100 <= mouse_x <= 1300 and 700 <= mouse_y <= 710 and walls_left > 0:
        wall = 'horizontal'
        turn_step = 2
    elif turn_step == 0 and 1500 <= mouse_x <= 1510 and 700 <= mouse_y <= 900 and walls_left > 0:
        wall = 'vertical'
        turn_step = 2
    elif wall:
        wall_pos_x, wall_pos_y = round(mouse_x / 100) * 100, round(mouse_y / 100) * 100
        if wall == 'horizontal':
            valid_wall_placement = (
                wall_pos_x / 100 in range(1, 9) and
                wall_pos_y / 100 in range(1, 11) and
                (wall_pos_x, wall_pos_y) not in horizontal_walls and
                (wall_pos_x + CELL_SIZE, wall_pos_y - CELL_SIZE) not in vertical_walls and
                is_winnable(red_pos[1] * CELL_SIZE + CELL_SIZE / 2 + 100, red_pos[0] * CELL_SIZE + CELL_SIZE / 2 + 100, horizontal_walls + [(wall_pos_x, wall_pos_y)], vertical_walls, 950) and
                is_winnable(yellow_pos[1] * CELL_SIZE + CELL_SIZE / 2 + 100, yellow_pos[0] * CELL_SIZE + CELL_SIZE / 2 + 100, horizontal_walls + [(wall_pos_x, wall_pos_y)], vertical_walls, 150)
            )
        elif wall == 'vertical':
            valid_wall_placement = (
                wall_pos_x / 100 in range(1, 11) and
                wall_pos_y / 100 in range(1, 9) and
                (wall_pos_x, wall_pos_y) not in vertical_walls and
                (wall_pos_x - CELL_SIZE, wall_pos_y + CELL_SIZE) not in horizontal_walls and
                is_winnable(red_pos[1] * CELL_SIZE + CELL_SIZE / 2 + 100, red_pos[0] * CELL_SIZE + CELL_SIZE / 2 + 100, horizontal_walls, vertical_walls + [(wall_pos_x, wall_pos_y)], 950) and
                is_winnable(yellow_pos[1] * CELL_SIZE + CELL_SIZE / 2 + 100, yellow_pos[0] * CELL_SIZE + CELL_SIZE / 2 + 100, horizontal_walls, vertical_walls + [(wall_pos_x, wall_pos_y)], 150)
            )

        if valid_wall_placement:
            if wall == 'horizontal':
                horizontal_walls.append((wall_pos_x, wall_pos_y))
            elif wall == 'vertical':
                vertical_walls.append((wall_pos_x, wall_pos_y))
            if player == 'red':
                red_walls -= 1
            else:
                yellow_walls -= 1
            wall = None
            player = opponent
            turn_step = 0
        else:
            wall = None
            turn_step = 0


pygame.init()

FONTS = {
    'MAIN_FONT': pygame.font.Font(pygame.font.get_default_font(), 36),
}

board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)] 
board[0][4]= 1
board[GRID_SIZE-1][4] =2

window_width = pygame.display.Info().current_w
window_height = pygame.display.Info().current_h
window = pygame.display.set_mode((window_width, window_height-80),pygame.RESIZABLE)
pygame.display.set_caption("Quoridor")

text_start = FONTS['MAIN_FONT'].render("START", True, COLORS['TEXT_PURPLE'])
text_exit = FONTS['MAIN_FONT'].render("EXIT", True, COLORS['TEXT_PURPLE'])


button_start = text_start.get_rect(
    center=(window_width // 2, window_height // 2))

button_exit = text_exit.get_rect(center=(window_width - 100, 50))


running = True
menu = True   
draw_grid = False 


red_pos = (0,4)
yellow_pos = (8, 4)
horizontal_walls = []
vertical_walls = []
turn_step = 0
valid_pawn_moves = []
valid_wall_moves = []
player = 'red'
red_walls = 10
yellow_walls = 10
wall = None


horizontal_x = [(x, x + 20) for x in range(90, 800, 100)]
horizontal_y = [(y, y + 20) for y in range(90, 900, 100)]
vertical_y = [(y, y + 20) for y in range(90, 800, 100)]
vertical_x = [(x, x + 20) for x in range(90, 910, 100)]

possible_ways = []
for x in range(9):
    for y in range(9):
        if y<8:
            possible_ways.append(((100*x + 150, 100*y + 150),(100*x + 150, 100 * (y+1) + 150)))
        if x<8:
            possible_ways.append(((100*x + 150 ,100*y + 150),(100*(x+1) + 150, 100*y + 150)))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            click_cords = (mouse_x // CELL_SIZE, mouse_y // CELL_SIZE)
            
            if button_start.collidepoint(event.pos):
                draw_grid = True
            elif button_exit.collidepoint(event.pos):
                running = False
            elif draw_grid:
                game_turn(click_cords)
                if 1680 <= mouse_x <= 1760 and 77 <= mouse_y <=120:
                    game = False
                    draw_grid = False
                    menu = True
                    red_pos = (0,4)
                    yellow_pos = (8, 4)
                    horizontal_walls = []
                    vertical_walls = []
                    turn_step = 0
                    valid_pawn_moves = []
                    valid_wall_moves = []
                    player = 'red'
                    red_walls = 10
                    yellow_walls = 10
                    wall = None
                

    window.fill(COLORS['PURPLE'])

    if menu:
        pygame.draw.rect(window, COLORS['LIGHT_PURPLE'], button_start)
        pygame.draw.rect(window, COLORS['LIGHT_PURPLE'], button_exit)
        window.blit(FONTS['MAIN_FONT'].render('Start', True, COLORS['WHITE']), button_start.topleft)
        window.blit(FONTS['MAIN_FONT'].render('Exit', True, COLORS['WHITE']), button_exit.topleft)

    if draw_grid:
        menu = False
        game = True
        draw_board()
        draw_players()
        
        if red_pos[0] == 8:
            game = False
            window.blit(FONTS['MAIN_FONT'].render('WINNER: RED', True, COLORS['WHITE']), (1100, 300))
        elif yellow_pos[0] == 0:
            game = False
            window.blit(FONTS['MAIN_FONT'].render('WINNER: YELLOW', True, COLORS['WHITE']), (1100, 300))
        for move in valid_pawn_moves:
            pygame.draw.circle(window, COLORS['GRAY'], (100 + move[1] * CELL_SIZE + CELL_SIZE // 2, 100 + move[0] * CELL_SIZE + CELL_SIZE // 2), 10)
        for fence in horizontal_walls:
            pygame.draw.line(window, COLORS['WHITE'], fence, (fence[0] + 200, fence[1]), 10)
        for fence in vertical_walls:
            pygame.draw.line(window, COLORS['WHITE'], fence, (fence[0], fence[1] + 200), 10)
        if wall:
            wall_x, wall_y = pygame.mouse.get_pos()
            if wall == 'horizontal':
                pygame.draw.rect(window, COLORS['WHITE'], (wall_x, wall_y, 200, 10))
            elif wall == 'vertical':
                pygame.draw.rect(window, COLORS['WHITE'], (wall_x, wall_y, 10, 200))

    pygame.display.flip()

pygame.quit()
sys.exit()
