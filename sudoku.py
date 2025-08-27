from multiprocessing import Process, Manager
import random
import time
from matplotlib import pyplot as plt

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
    if num in board[i]:
        return False
    if any(board[row][j] == num for row in range(9)):
        return False
    start_row = (i // 3) * 3
    start_col = (j // 3) * 3
    for row in range(start_row, start_row + 3):
        for col in range(start_col, start_col + 3):
            if board[row][col] == num:
                return False
    return True

def backtrack_custom_aléatoire(board, solutions, afficher=False, ordre=None, stop_flag=None):
    if stop_flag and stop_flag.value:
        return
    if solutions:
        if stop_flag:
            stop_flag.value = True
        return

    cell = trouver_case_mrv(board)
    if not cell:
        solutions.append([row[:] for row in board])
        if stop_flag:
            stop_flag.value = True
        return

    i, j = cell
    chiffres = ordre if ordre else list(range(1, 10))

    for num in chiffres:
        if est_valide(board, i, j, num):
            board[i][j] = num
            backtrack_custom_aléatoire(board, solutions, afficher, ordre, stop_flag)
            board[i][j] = 0

def resolution(copie, ordre, shared_solutions, stop_flag, temps_resolution):
    start = time.time()
    local_solutions = []
    backtrack_custom_aléatoire(copie, local_solutions, afficher=False, ordre=ordre, stop_flag=stop_flag)
    stop = time.time()
    temps = stop - start
    if local_solutions:
        shared_solutions.append(local_solutions[0])
        stop_flag.value = True
        temps_resolution.append(temps)



def creer_process(board, shared_solutions, stop_flag, temps_resolution):
    copie = [row[:] for row in board]
    ordre = list(range(1, 10))
    random.shuffle(ordre)
    return Process(target=resolution, args=(copie, ordre, shared_solutions, stop_flag, temps_resolution))


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
    import pygame
    pygame.init()
    WIDTH, HEIGHT = 540, 540
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Affichage Sudoku")
    FONT = pygame.font.SysFont("comicsans", 40)
    manager = Manager()
    shared_solutions = manager.list()
    temps_resolution = manager.list()
    stop_flag = manager.Value('b', False)
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
                if event.key == pygame.K_SPACE and not resolution_lancée :
                    resolution_lancée = True
                    stop_flag.value = False
                    shared_solutions[:] = []
                    temps_resolution[:] = []
                    for _ in range(2):  # Tu peux ajuster le nombre de processus ici
                        p = creer_process(board, shared_solutions, stop_flag, temps_resolution)
                        p.start()
                        processes.append(p)
                    start = time.time()
                elif event.key != pygame.K_SPACE :
                    running = False

        if resolution_lancée and all(not p.is_alive() for p in processes):
            stop = time.time()
            resolution_lancée = False
            for p in processes:
                p.join()
            processes.clear()
            temps = stop - start
            print(f"Résolution terminée en {temps} secondes")
            print(f"✅ Temps du processus ayant trouvé la solution : {temps_resolution[0]} secondes")
            if shared_solutions:
                WIN.fill((255, 255, 255))
                draw_grid(WIN, WIDTH, HEIGHT)
                draw_numbers(WIN, shared_solutions[0], FONT, WIDTH)
                pygame.display.update()
                print("Solution affichée.")
            else:
                print("Aucune solution disponible.")


def test(proces, rep):
    vals = []
    for i in range(rep):
        manager = Manager()
        shared_solutions = manager.list()
        temps_resolution = manager.list()
        stop_flag = manager.Value('b', False)
        processes = []

        stop_flag.value = False
        shared_solutions[:] = []
        temps_resolution[:] = []

        for _ in range(proces):
            p = creer_process(board, shared_solutions, stop_flag, temps_resolution)
            p.start()
            processes.append(p)

        # Attendre que tous les processus soient terminés
        while not all(not p.is_alive() for p in processes):
            time.sleep(0.01)
        for p in processes:
            p.join()
        processes.clear()
        if temps_resolution:
            vals.append(temps_resolution[0])
            print(temps_resolution[0])

    if vals:
        print(f"\n📊 Résumé pour {rep} tests avec {proces} processus :")
        print(f"Temps moyen : {sum(vals)/len(vals):.4f} secondes")
        print(f"Temps minimum : {min(vals):.4f} secondes")
        print(f"Temps maximum : {max(vals):.4f} secondes")
        plt.figure()
        y = vals
        plt.plot(y, label='vals', color='blue', marker='o')
        plt.title(f'bench sudoku pour {rep} tests avec {proces} processus :')
        plt.show(block=False)

    else:
        print("❌ Aucun temps enregistré")
if __name__ == "__main__":
    test(1, 20)
    test(2, 20)
    test(4, 20)
    test(10, 20)
    while input("stop Y/N") != "Y":
        time.sleep(1)
