import pygame
from multiprocessing import Process, Manager
import random


# Exemple de grille (0 = case vide)
board = [
    [0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 2, 0, 0, 0],
    [0, 0, 0, 3, 0, 0, 0, 0, 0],
    [0, 0, 4, 0, 0, 0, 0, 0, 0],
    [5, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 6, 0, 0],
    [0, 0, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 8, 0, 0, 0, 0, 0],
    [9, 0, 0, 0, 0, 0, 0, 0, 0]
]


def detect_carre(x,y):
    if x <= 2:
        if y <= 2:
            return 0
        elif y >=2 and y <=5:
            return 1
        elif y >= 5:
            return 2
    elif x >=2 and x <=5:
        if y <= 2:
            return 3
        elif y >=2 and y <=5:
            return 4
        elif y >= 5:
            return 5
    elif x >=5:
        if y <= 2:
            return 6
        elif y >=2 and y <=5:
            return 7
        elif y >= 5:
            return 8

def decoupe_carres(board):
    carres = []
    for box_row in range(3):
        for box_col in range(3):
            carre = []
            for i in range(3):
                for j in range(3):
                    row = box_row * 3 + i
                    col = box_col * 3 + j
                    carre.append(board[row][col])
            carres.append(carre)
    return carres

def decoupe_colonnes(board):
    colonnes = []
    for col in range(9):
        colonne = []
        for row in range(9):
            colonne.append(board[row][col])
        colonnes.append(colonne)
    return colonnes


def test_number_sudoku(num, board):
    solutions = []
    carres = decoupe_carres(board)
    colonnes = decoupe_colonnes(board)

    for i in range(9):  # lignes
        for j in range(9):  # colonnes
            if board[i][j] == 0:  # case vide
                ligne = board[i]
                colonne = colonnes[j]
                carre_index = detect_carre(i, j)
                carre = carres[carre_index]

                if num not in ligne and num not in colonne and num not in carre:
                    solutions.append((i, j))  # position valide
    return solutions

def trouver_case_mrv(board):
    min_options = 10
    best_cell = None
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                options = [num for num in range(1, 10) if est_valide(board, i, j, num)]
                if len(options) < min_options:
                    min_options = len(options)
                    best_cell = (i, j)
    return best_cell

def est_valide(board, i, j, num):
    # Vérifie si num est déjà dans la ligne
    if num in board[i]:
        return False

    # Vérifie si num est déjà dans la colonne
    for row in range(9):
        if board[row][j] == num:
            return False

    # Vérifie si num est déjà dans le carré 3x3
    start_row = (i // 3) * 3
    start_col = (j // 3) * 3
    for row in range(start_row, start_row + 3):
        for col in range(start_col, start_col + 3):
            if board[row][col] == num:
                return False

    # Si aucune contrainte violée, c'est valide
    return True

def backtrack_custom_aléatoire(board, solutions, afficher=False, ordre=None):
    if solutions:
        return

    cell = trouver_case_mrv(board)
    if not cell:
        solutions.append([row[:] for row in board])
        return

    i, j = cell
    chiffres = ordre if ordre else list(range(1, 10))

    for num in chiffres:
        if est_valide(board, i, j, num):
            board[i][j] = num
            backtrack_custom_aléatoire(board, solutions, afficher, ordre)
            board[i][j] = 0


def resolution(copie, ordre, shared_solutions):
    local_solutions = []
    backtrack_custom_aléatoire(copie, local_solutions, afficher=False, ordre=ordre)
    if local_solutions:
        shared_solutions.append(local_solutions[0])

def creer_process(board, shared_solutions):
    copie = [row[:] for row in board]
    ordre = list(range(1, 10))
    random.shuffle(ordre)
    return Process(target=resolution, args=(copie, ordre, shared_solutions))






# Fonction pour dessiner la grille
def draw_grid(win, width, height):
    gap = width // 9
    for i in range(10):
        thickness = 3 if i % 3 == 0 else 1
        pygame.draw.line(win, (0, 0, 0), (0, i * gap), (width, i * gap), thickness)
        pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, height), thickness)

def draw_numbers(win, board, font, width):
    gap = width // 9
    for i in range(9):
        for j in range(9):
            num = board[i][j]
            if num != 0:
                text = font.render(str(num), True, (0, 0, 0))
                win.blit(text, (j * gap + 20, i * gap + 10))

def main():
    # Initialisation
    pygame.init()
    WIDTH, HEIGHT = 540, 540
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Affichage Sudoku")
    FONT = pygame.font.SysFont("comicsans", 40)
    manager = Manager()
    shared_solutions = manager.list()
    processes = []

    running = True
    resolution_lancée = False

    WIN.fill((255, 255, 255))
    draw_grid(WIN, WIDTH, HEIGHT)
    draw_numbers(WIN, board, FONT, WIDTH)
    pygame.display.update()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not resolution_lancée:
                    resolution_lancée = True
                    for _ in range(10):
                        p = creer_process(board, shared_solutions)
                        p.start()
                        processes.append(p)
                else: 
                    running = False

        if resolution_lancée and all(not p.is_alive() for p in processes):
            resolution_lancée = False  # Empêche relancement
            for p in processes:
                p.join()
                processes.clear()
            print("Résolution terminée.")
            if shared_solutions:
                WIN.fill((255, 255, 255))
                draw_grid(WIN, WIDTH, HEIGHT)
                draw_numbers(WIN, shared_solutions[0], FONT, WIDTH)
                pygame.display.update()
                print("Solution affichée.")
            else:
                print("Aucune solution disponible.")


if __name__ == '__main__':
    main()