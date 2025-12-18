
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dames internationales 10x10 - Pygame
- Plateau 10x10
- Prises obligatoires
- Prise la plus longue obligatoire
- Dames (kings) se déplacent/capturent sur diagonale entière
- Interface simple : menu, sélection par clic, surbrillance
"""

import pygame
import sys
from copy import deepcopy

# --- Configuration visuelle ---
TAILLE_CASE = 64
NB_CASES = 10
LARGEUR = HAUTEUR = TAILLE_CASE * NB_CASES
FPS = 60

# Couleurs
BEIGE = (245, 222, 179)
MARRON = (139, 69, 19)
NOIR = (0, 0, 0)
BLANC = (250, 250, 250)
ROUGE = (220, 50, 50)
VERT = (50, 180, 50)
OR = (212, 175, 55)
GRIS = (200, 200, 200)

pygame.init()
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR + 60))  # espace pour boutons/messages
pygame.display.set_caption("Dames internationales 10x10")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)
big_font = pygame.font.SysFont("arial", 34)

# --- Utilitaires coord / board ---
def in_bounds(x, y):
    return 0 <= x < NB_CASES and 0 <= y < NB_CASES

def opp(player):
    return 'b' if player == 'w' else 'w'

# Board: 2D list, rows y=0..9 top->bottom, x=0..9 left->right
# Pieces: 'b' (black man), 'B' (black king), 'w' (white man), 'W' (white king), '.' empty

def initial_board():
    board = [['.' for _ in range(NB_CASES)] for _ in range(NB_CASES)]
    # International setup: 4 rows for each side on dark squares
    for y in range(0, 4):
        for x in range(NB_CASES):
            if (x + y) % 2 == 1:
                board[y][x] = 'w'   # white at top (convention: white moves down)
    for y in range(6, 10):
        for x in range(NB_CASES):
            if (x + y) % 2 == 1:
                board[y][x] = 'b'   # black at bottom (black moves up)
    return board

# --- Move generation with captures (longest capture rule) ---
# Directions
DIAGS = [(-1, -1), (1, -1), (-1, 1), (1, 1)]

def is_enemy(piece, player):
    if piece == '.': return False
    return piece.lower() != player

def is_friend(piece, player):
    if piece == '.': return False
    return piece.lower() == player

def generate_capture_sequences(board, x, y, player):
    """
    Return list of capture sequences from (x,y).
    Each sequence is a list of positions (x,y) visited including start and successive landings.
    Also return the set/list of captured piece coords per sequence (but we can infer captured count).
    We will produce sequences that do not re-capture the same piece.
    """
    piece = board[y][x]
    king = piece.isupper()

    sequences = []

    def dfs_man(bd, cx, cy, seq, captured_set):
        moved = False
        for dx, dy in DIAGS:
            mx, my = cx + dx, cy + dy
            lx, ly = cx + 2*dx, cy + 2*dy
            if in_bounds(mx, my) and in_bounds(lx, ly):
                if is_enemy(bd[my][mx], player) and bd[ly][lx] == '.' and (mx,my) not in captured_set:
                    # simulate capture
                    nb = deepcopy(bd)
                    nb[cy][cx] = '.'
                    nb[my][mx] = '.'
                    nb[ly][lx] = piece
                    dfs_man(nb, lx, ly, seq + [(lx,ly)], captured_set | {(mx,my)})
                    moved = True
        if not moved:
            if len(seq) > 1:
                sequences.append(seq)

    def dfs_king(bd, cx, cy, seq, captured_set):
        moved = False
        for dx, dy in DIAGS:
            sx, sy = cx + dx, cy + dy
            while in_bounds(sx, sy) and bd[sy][sx] == '.':
                sx += dx; sy += dy
            # now either out of bounds or on first non-empty
            if in_bounds(sx, sy) and is_enemy(bd[sy][sx], player) and (sx,sy) not in captured_set:
                # we can capture this enemy, and land on any empty square beyond it
                tx, ty = sx + dx, sy + dy
                while in_bounds(tx, ty):
                    if bd[ty][tx] != '.':
                        break
                    # simulate capture landing at (tx,ty)
                    nb = deepcopy(bd)
                    nb[cy][cx] = '.'
                    nb[sy][sx] = '.'
                    nb[ty][tx] = piece
                    dfs_king(nb, tx, ty, seq + [(tx,ty)], captured_set | {(sx,sy)})
                    moved = True
                    tx += dx; ty += dy
        if not moved:
            if len(seq) > 1:
                sequences.append(seq)

    if king:
        dfs_king(board, x, y, [(x,y)], set())
    else:
        dfs_man(board, x, y, [(x,y)], set())
    return sequences

def count_captured_from_seq(seq, start_board):
    # infer captured pieces by simulating along seq
    b = deepcopy(start_board)
    sx, sy = seq[0]
    piece = b[sy][sx]
    captured = 0
    for i in range(1, len(seq)):
        tx, ty = seq[i]
        px, py = seq[i-1]
        if abs(tx - px) == 2 or abs(ty - py) == 2:
            mx, my = (tx + px)//2, (ty + py)//2
            if b[my][mx] != '.':
                b[my][mx] = '.'
                captured += 1
        else:
            # for king long jump: find the captured piece between px,py and tx,ty
            dx = 1 if tx > px else -1
            dy = 1 if ty > py else -1
            cx, cy = px + dx, py + dy
            while (cx, cy) != (tx, ty):
                if b[cy][cx] != '.':
                    b[cy][cx] = '.'
                    captured += 1
                    break
                cx += dx; cy += dy
        # move piece
        b[sy][sx] = '.'
        b[ty][tx] = piece
        sx, sy = tx, ty
    return captured

def all_moves_for_player(board, player):
    """Return two lists: capture_moves, quiet_moves.
    capture_moves: list of sequences (path lists) for all player's pieces.
    quiet_moves: list of simple moves [ (x1,y1,x2,y2) ] if no capture exists anywhere.
    """
    capture_moves = []
    for y in range(NB_CASES):
        for x in range(NB_CASES):
            if is_friend(board[y][x], player):
                seqs = generate_capture_sequences(board, x, y, player)
                for s in seqs:
                    capture_moves.append(( (x,y), s ))
    if capture_moves:
        # apply longest-capture rule: keep only sequences with maximum captured count
        max_captured = 0
        enriched = []
        for origin, seq in capture_moves:
            c = count_captured_from_seq(seq, board)
            enriched.append((origin, seq, c))
            if c > max_captured: max_captured = c
        filtered = [(o,s) for (o,s,c) in enriched if c == max_captured]
        return filtered, []
    # no captures anywhere -> quiet moves
    quiet = []
    for y in range(NB_CASES):
        for x in range(NB_CASES):
            p = board[y][x]
            if is_friend(p, player):
                king = p.isupper()
                if king:
                    for dx,dy in DIAGS:
                        tx, ty = x + dx, y + dy
                        while in_bounds(tx,ty):
                            if board[ty][tx] == '.':
                                quiet.append((x,y,tx,ty))
                                tx += dx; ty += dy
                            else:
                                break
                else:
                    # man moves one step forward only (in international convention: men move forward toward opponent)
                    # Convention chosen earlier: white at top moves down (dy=+1), black at bottom moves up (dy=-1)
                    direction = 1 if p == 'w' else -1
                    for dx in (-1,1):
                        tx, ty = x + dx, y + direction
                        if in_bounds(tx, ty) and board[ty][tx] == '.':
                            quiet.append((x,y,tx,ty))
    return [], quiet

# --- Apply moves (including performing captures along chosen sequence) ---
def apply_sequence(board, seq):
    """Apply capture sequence seq (list of positions), modify board, handle promotion."""
    b = board
    sx, sy = seq[0]
    piece = b[sy][sx]
    b[sy][sx] = '.'
    for i in range(1, len(seq)):
        tx, ty = seq[i]
        px, py = seq[i-1]
        # remove captured piece between px,py and tx,ty
        if abs(tx - px) == 2 and abs(ty - py) == 2:
            mx, my = (tx + px)//2, (ty + py)//2
            b[my][mx] = '.'
        else:
            # king capture: find first enemy along line
            dx = 1 if tx > px else -1
            dy = 1 if ty > py else -1
            cx, cy = px + dx, py + dy
            while (cx, cy) != (tx, ty):
                if b[cy][cx] != '.':
                    b[cy][cx] = '.'
                    break
                cx += dx; cy += dy
        # move piece
        # clear previous pos for iterative simulation
        b[py][px] = '.'
        b[ty][tx] = piece
    # promotion
    final_x, final_y = seq[-1]
    if piece == 'w' and final_y == NB_CASES - 1:
        b[final_y][final_x] = 'W'
    if piece == 'b' and final_y == 0:
        b[final_y][final_x] = 'B'

def apply_quiet_move(board, x1, y1, x2, y2):
    piece = board[y1][x1]
    board[y1][x1] = '.'
    board[y2][x2] = piece
    if piece == 'w' and y2 == NB_CASES - 1:
        board[y2][x2] = 'W'
    if piece == 'b' and y2 == 0:
        board[y2][x2] = 'B'

# --- Drawing ---
def draw_board(surface, board, selected, highlights):
    # board area
    for y in range(NB_CASES):
        for x in range(NB_CASES):
            rect = pygame.Rect(x*TAILLE_CASE, y*TAILLE_CASE, TAILLE_CASE, TAILLE_CASE)
            color = BEIGE if (x+y)%2==0 else MARRON
            pygame.draw.rect(surface, color, rect)
            # highlight possible landing squares
            if (x,y) in highlights:
                pygame.draw.rect(surface, (150,220,150), rect)
            # selection frame
            if selected == (x,y):
                pygame.draw.rect(surface, ROUGE, rect, 3)
            # pieces
            piece = board[y][x]
            if piece != '.':
                center = (x*TAILLE_CASE + TAILLE_CASE//2, y*TAILLE_CASE + TAILLE_CASE//2)
                r = TAILLE_CASE//2 - 6
                if piece.lower() == 'b':
                    pygame.draw.circle(surface, NOIR, center, r)
                else:
                    pygame.draw.circle(surface, BLANC, center, r)
                if piece.isupper():
                    pygame.draw.circle(surface, OR, center, r//2)

def draw_ui(surface, current_player, message, show_buttons=True):
    # bottom bar
    bar_rect = pygame.Rect(0, HAUTEUR, LARGEUR, 60)
    pygame.draw.rect(surface, GRIS, bar_rect)
    text = f"Joueur: {'Noir ⚫' if current_player=='b' else 'Blanc ⚪'}"
    surf = font.render(text, True, NOIR)
    surface.blit(surf, (8, HAUTEUR + 8))
    if message:
        surf2 = font.render(message, True, ROUGE)
        surface.blit(surf2, (200, HAUTEUR + 8))
    if show_buttons:
        # Buttons: Rejouer, Menu Quitter (we put them top-right)
        btn_w, btn_h = 100, 36
        # Rejouer
        replay_rect = pygame.Rect(LARGEUR - 220, HAUTEUR + 12, btn_w, btn_h)
        menu_rect = pygame.Rect(LARGEUR - 110, HAUTEUR + 12, btn_w, btn_h)
        pygame.draw.rect(surface, (180,180,180), replay_rect)
        pygame.draw.rect(surface, (180,180,180), menu_rect)
        surface.blit(font.render("Rejouer", True, NOIR), (LARGEUR - 200, HAUTEUR + 20))
        surface.blit(font.render("Quitter", True, NOIR), (LARGEUR - 85, HAUTEUR + 20))
        return replay_rect, menu_rect
    return None, None

# --- Menu ---
def draw_menu(surface):
    surface.fill(BEIGE)
    title = big_font.render("Dames internationales (10x10)", True, NOIR)
    surface.blit(title, (LARGEUR//2 - title.get_width()//2, 80))
    # Buttons: Jouer / Quitter
    btn_play = pygame.Rect(LARGEUR//2 - 80, 200, 160, 50)
    btn_quit = pygame.Rect(LARGEUR//2 - 80, 270, 160, 50)
    pygame.draw.rect(surface, (180,180,180), btn_play)
    pygame.draw.rect(surface, (180,180,180), btn_quit)
    surface.blit(font.render("Jouer", True, NOIR), (LARGEUR//2 - 20, 215))
    surface.blit(font.render("Quitter", True, NOIR), (LARGEUR//2 - 24, 285))
    return btn_play, btn_quit

# --- Game loop state machine ---
def game_loop():
    board = initial_board()
    current = 'b'  # black starts (convention)
    selected = None
    highlights = set()
    capture_options = {}  # map origin -> list of sequences (max sequences only)
    quiet_options = []
    message = ""
    game_over = False

    def recompute_options():
        nonlocal capture_options, quiet_options
        cap, quiet = all_moves_for_player(board, current)
        # cap: list of (origin, seq) but filtered by max captures in function
        capture_options = {}
        for origin, seq in cap:
            capture_options.setdefault(origin, []).append(seq)
        quiet_options = quiet

    recompute_options()

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # If click in board area
                if my < HAUTEUR:
                    cx, cy = mx // TAILLE_CASE, my // TAILLE_CASE
                    if not game_over:
                        # If there's capture anywhere, only allow selecting pieces that have capture sequences
                        if selected is None:
                            # select a piece of current player that has moves
                            if (cx,cy) in capture_options or any((cx==o[0] and cy==o[1]) for o in [(o[0],o[1]) for o in capture_options.keys()]):
                                # if piece has capture sequences
                                if (cx,cy) in capture_options:
                                    selected = (cx,cy)
                                    # allowed first-step landing squares = all first-step positions among sequences
                                    highlights = set(seq[1] for seq in capture_options[selected])
                                else:
                                    # If no captures anywhere, allow quiet moves
                                    if not capture_options:
                                        # check quiet moves from this piece
                                        tmp = [ (x1,y1,x2,y2) for (x1,y1,x2,y2) in quiet_options if x1==cx and y1==cy]
                                        if tmp:
                                            selected = (cx,cy)
                                            highlights = set((x2,y2) for (_,_,x2,y2) in tmp)
                            else:
                                # no captures required or selecting a quiet move piece
                                if not capture_options:
                                    # allow select current player's piece with quiet moves
                                    if is_friend(board[cy][cx], current):
                                        # check has quiet moves
                                        tmp = [ (x1,y1,x2,y2) for (x1,y1,x2,y2) in quiet_options if x1==cx and y1==cy]
                                        if tmp:
                                            selected = (cx,cy)
                                            highlights = set((x2,y2) for (_,_,x2,y2) in tmp)
                                else:
                                    # there are captures but clicked non-capturing piece -> ignore / flash
                                    pass
                        else:
                            # a piece already selected, check if clicked on one of highlights
                            if (cx,cy) in highlights:
                                # If there are capture options, we must follow capture sequences for this origin
                                if selected in capture_options:
                                    # Find sequences that have this cell as next landing (prefix match)
                                    possible = [seq for seq in capture_options[selected] if seq[1] == (cx,cy)]
                                    if not possible:
                                        # maybe clicked a landing that is part of sequence but not first-step; reject
                                        selected = None
                                        highlights = set()
                                    else:
                                        # perform the first jump chosen: apply the first step only.
                                        # We then need to continue the forced capture from new position, but only among sequences that were maxima.
                                        chosen_seq = possible[0]  # note: multiple sequences may share same first step; keep set of remaining sequences
                                        # To allow user to choose among multiple maximal sequences sharing same first step, we keep all matching sequences
                                        # Apply the first move (simulate removal of captured piece between)
                                        prev = selected
                                        # compute intermediate board change for that first step
                                        # We'll simulate by applying sequence truncated to first step (seq[0], seq[1])
                                        sub = [chosen_seq[0], chosen_seq[1]]
                                        apply_sequence(board, sub)
                                        # After applying, compute remaining sequences consistent with chosen first-step:
                                        # We need to build new capture_options for continuing capture from current landing
                                        new_x, new_y = chosen_seq[1]
                                        # Build sequences that start with chosen_seq and continue (i.e. sequences from capture_options[selected] that had that prefix),
                                        # but we must adjust for captured pieces already removed; recompute full sequences from current landing
                                        # To allow choices among continuing maxima, we recompute all sequences from this new position on the new board,
                                        # but restrict to those that continue from same origin path length remaining and that combined reach the same global max captured count.
                                        # Simpler robust approach: recompute all capture sequences from new position, compute max captured remaining, and let
                                        # player continue until no more captures. Because we had enforced global max before first step, any continuation that stops earlier
                                        # would not reach global max; but since we removed pieces according to the first step, sequences that achieve remaining max are valid.
                                        # So we recompute
                                        selected = (new_x, new_y)
                                        recompute_options()
                                        # Now restrict: we only want capture sequences that originate from this selected pos; highlights = next-step landings among these sequences
                                        if selected in capture_options:
                                            highlights = set(seq[1] for seq in capture_options[selected])
                                        else:
                                            # no further captures -> end of turn
                                            selected = None
                                            highlights = set()
                                            # switch player
                                            current = opp(current)
                                            recompute_options()
                                else:
                                    # quiet move case
                                    x1,y1 = selected
                                    apply_quiet_move(board, x1, y1, cx, cy)
                                    selected = None
                                    highlights = set()
                                    current = opp(current)
                                    recompute_options()
                            else:
                                # clicked elsewhere -> cancel selection
                                selected = None
                                highlights = set()
                    else:
                        # game over -> ignore board clicks
                        pass
                else:
                    # click in UI area -> check buttons
                    replay_rect = pygame.Rect(LARGEUR - 220, HAUTEUR + 12, 100, 36)
                    quit_rect = pygame.Rect(LARGEUR - 110, HAUTEUR + 12, 100, 36)
                    if replay_rect.collidepoint(mx,my):
                        return 'replay'
                    if quit_rect.collidepoint(mx,my):
                        return 'quit'

        # check end condition: no moves for current player -> opponent wins
        cap, quiet = all_moves_for_player(board, current)
        if not cap and not quiet and not game_over:
            message = f"{'Noir' if current=='b' else 'Blanc'} n'a plus de coups. { 'Blanc' if current=='b' else 'Noir'} gagne !"
            game_over = True

        # draw
        fenetre.fill((100,100,100))
        draw_board(fenetre, board, selected, highlights)
        replay_rect, quit_rect = draw_ui(fenetre, current, message, show_buttons=True)
        pygame.display.flip()

def main_menu_loop():
    while True:
        clock.tick(FPS)
        fenetre.fill(BEIGE)
        btn_play, btn_quit = draw_menu(fenetre)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_play.collidepoint(event.pos):
                    return 'play'
                if btn_quit.collidepoint(event.pos):
                    pygame.quit(); sys.exit()

def main():
    while True:
        action = main_menu_loop()
        if action == 'play':
            result = game_loop()
            if result == 'quit':
                pygame.quit(); sys.exit()
            # if replay, loop continues
        else:
            pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()
