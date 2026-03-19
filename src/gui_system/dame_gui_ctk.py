# -*- coding: utf-8 -*-
"""
Interface graphique du Jeu de Dames avec CustomTkinter.
Utilise les fonctions de damedemain.py sans les modifier.
Tous les appels aux fonctions damedemain sont tracés dans la zone de log.
"""

import sys
import os
import json
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from damedemain import is_friendly, jeu_possible, team_exist

try:
    import winsound
    _HAS_WINSOUND = True
except ImportError:
    _HAS_WINSOUND = False

DIAGS = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
SQUARE_SIZE = 70
LOG_HEIGHT = 200
PIECE_FONT = 48

DARK_SQ = "#8B4513"
LIGHT_SQ = "#DEB887"
HL_PIECE = "#4a7c59"
HL_MOVE = "#7FDB7F"
HL_CAPTURE = "#c45c26"
HL_CAPTURE_LAND = "#7FDB7F"
CLR_NOIR = "#1E90FF"
CLR_BLANC = "#DC143C"

BEEP_FREQ = 600
BEEP_DURATION = 80


def log_call(gui, name: str, args: tuple, result):
    gui.append_log(f"→ {name}({', '.join(str(a) for a in args)}) = {result}")


def create_board(c, l, N):
    L = [[[0, 0, (1 + h % 2 - g % 2) % 2] for g in range(l)] for h in range(c)]
    for i in range(c):
        for k in range(l):
            if i < N and L[i][k][2] == 1:
                L[i][k][0], L[i][k][1] = 1, 1
            elif i > c - N - 1 and L[i][k][2] == 1:
                L[i][k][0], L[i][k][1] = 2, 1
    return L


def get_moves(L, col, ligne, J, v):
    """Convertit le retour de jeu_possible en liste de (to_col, to_ligne, is_capture).
    Blancs (v=0) avancent vers cols basses → diags 0,2 ; Noirs (v=1) vers cols hautes → diags 1,3.
    Captures autorisées dans les 4 directions (règle jeu de dames).
    """
    if not J:
        return []
    moves = []
    if isinstance(J[0], list):
        for tc in range(len(J)):
            for tl in range(len(J[0])):
                if J[tc][tl] == 1:
                    moves.append((tc, tl, True))
                elif J[tc][tl] == 2:
                    moves.append((tc, tl, False))
    else:
        forward = [0, 2] if v == 0 else [1, 3]
        for i in range(4):
            if J[i] == 1:
                moves.append((col + 2 * DIAGS[i][0], ligne + 2 * DIAGS[i][1], True))
            elif J[i] == 2 and i in forward:
                moves.append((col + DIAGS[i][0], ligne + DIAGS[i][1], False))
    return moves


def do_move(L, fc, fl, tc, tl, capture):
    """Exécute un mouvement. Retourne (col, ligne) de la pièce capturée ou None."""
    piece = L[fc][fl].copy()
    L[fc][fl] = [0, 0, L[fc][fl][2]]
    captured = None
    if capture:
        dc = 1 if tc > fc else -1
        dl = 1 if tl > fl else -1
        sc, sl = fc + dc, fl + dl
        while (sc, sl) != (tc, tl):
            if L[sc][sl][0] != 0:
                L[sc][sl][0], L[sc][sl][1] = 0, 0
                captured = (sc, sl)
                break
            sc += dc
            sl += dl
    L[tc][tl][0], L[tc][tl][1] = piece[0], piece[1]
    return captured


class DameGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jeu de Dames")
        self.resizable(True, True)

        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(root_dir)
        config_path = None
        for base in (project_root, root_dir, os.getcwd()):
            p = os.path.join(base, "config", "regle.json")
            if os.path.exists(p):
                config_path = p
                break
        if config_path:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)[0]
                self.c = cfg.get("colonne", 8)
                self.l = cfg.get("ligne", 8)
                self.N = cfg.get("ligne_de_pion", 3)
        else:
            self.c, self.l, self.N = 8, 8, 3

        self.L = create_board(self.c, self.l, self.N)
        self.current_player = 1
        self.hover_piece = None
        self.hover_moves = []
        self._game_over = False
        self._clear_timer = None

        board_px = max(self.c, self.l) * SQUARE_SIZE
        self.geometry(f"{board_px + 40}x{board_px + LOG_HEIGHT + 100}")
        try:
            self.state("zoomed")
        except Exception:
            pass

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        self.label_tour = ctk.CTkLabel(
            main, text="Tour des Noirs", font=("Arial", 22, "bold")
        )
        self.label_tour.pack(pady=(0, 5))

        board_frame = ctk.CTkFrame(main, fg_color="#2b2b2b", corner_radius=4)
        board_frame.pack()
        board_frame.bind("<Leave>", lambda e: self._schedule_clear())

        self.squares = []
        for ligne in range(self.l):
            row = []
            for col in range(self.c):
                base = DARK_SQ if self.L[col][ligne][2] == 1 else LIGHT_SQ
                sq = ctk.CTkButton(
                    board_frame,
                    width=SQUARE_SIZE - 2,
                    height=SQUARE_SIZE - 2,
                    text="",
                    font=("Arial", PIECE_FONT),
                    fg_color=base,
                    hover_color=base,
                    text_color="#FFFFFF",
                    command=lambda c=col, l=ligne: self._on_click(c, l),
                )
                sq.bind("<Enter>", lambda e, c=col, l=ligne: self._on_enter(c, l))
                sq.grid(row=ligne, column=col, padx=1, pady=1)
                row.append(sq)
            self.squares.append(row)

        self._draw_all_pieces()

        log_frame = ctk.CTkFrame(main, fg_color="#1a1a1a", corner_radius=4)
        log_frame.pack(fill="x", pady=(10, 0))
        ctk.CTkLabel(
            log_frame, text="Journal des appels (log)", font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=12, pady=(8, 4))
        self.log_text = ctk.CTkTextbox(
            log_frame, height=LOG_HEIGHT, font=("Consolas", 14), state="disabled"
        )
        self.log_text.pack(fill="x", padx=12, pady=(0, 12))

        self.append_log("=== Démarrage du jeu ===")
        self._log_teams()

    # ── rendering (targeted) ──

    def _base_color(self, col, ligne):
        return DARK_SQ if self.L[col][ligne][2] == 1 else LIGHT_SQ

    def _piece_txt(self, col, ligne):
        p = self.L[col][ligne]
        if p[0] == 1:
            return ("♔" if p[1] == 2 else "●", CLR_NOIR)
        if p[0] == 2:
            return ("♕" if p[1] == 2 else "●", CLR_BLANC)
        return ("", "#FFFFFF")

    def _set_bg(self, col, ligne, bg=None):
        if bg is None:
            bg = self._base_color(col, ligne)
        self.squares[ligne][col].configure(fg_color=bg, hover_color=bg)

    def _draw_cell(self, col, ligne, bg=None):
        self._set_bg(col, ligne, bg)
        txt, tc = self._piece_txt(col, ligne)
        self.squares[ligne][col].configure(text=txt, text_color=tc)

    def _draw_all_pieces(self):
        for col in range(self.c):
            for ligne in range(self.l):
                txt, tc = self._piece_txt(col, ligne)
                self.squares[ligne][col].configure(text=txt, text_color=tc)

    # ── hover (only touches affected cells) ──

    def _apply_hover(self, piece, moves):
        """Clear old highlights, apply new ones. Only updates changed cells."""
        old = set()
        if self.hover_piece:
            old.add(self.hover_piece)
        for m in self.hover_moves:
            old.add((m[0], m[1]))

        new_map = {}
        if piece:
            new_map[piece] = HL_PIECE
        for m in moves:
            new_map[(m[0], m[1])] = HL_MOVE

        self.hover_piece = piece
        self.hover_moves = moves

        for cell in old:
            if cell not in new_map:
                self._set_bg(cell[0], cell[1])
        for cell, color in new_map.items():
            self._set_bg(cell[0], cell[1], color)

    def _clear_hover(self):
        if self.hover_piece or self.hover_moves:
            self._apply_hover(None, [])

    def _schedule_clear(self):
        """board_frame Leave → schedule clear (cancelled if Enter fires on a child)."""
        if self._clear_timer:
            self.after_cancel(self._clear_timer)
        self._clear_timer = self.after(60, self._do_scheduled_clear)

    def _do_scheduled_clear(self):
        self._clear_timer = None
        self._clear_hover()

    def _cancel_clear(self):
        if self._clear_timer:
            self.after_cancel(self._clear_timer)
            self._clear_timer = None

    def _on_enter(self, col, ligne):
        self._cancel_clear()
        if self._game_over:
            return
        dests = {(m[0], m[1]) for m in self.hover_moves}
        if (col, ligne) in dests or (col, ligne) == self.hover_piece:
            return

        v = 1 if self.current_player == 1 else 0
        if is_friendly(self.L, col, ligne, v):
            J = jeu_possible(self.L, col, ligne, DIAGS, v, None)
            moves = get_moves(self.L, col, ligne, J, v)
            self._apply_hover((col, ligne), moves)

    # ── click ──

    def _on_click(self, col, ligne):
        if self._game_over:
            return
        dest = next((m for m in self.hover_moves if m[0] == col and m[1] == ligne), None)
        if not dest or not self.hover_piece:
            return

        fc, fl = self.hover_piece
        tc, tl, is_cap = dest
        v = 1 if self.current_player == 1 else 0

        log_call(self, "is_friendly", ("L", fc, fl, v), True)
        J = jeu_possible(self.L, fc, fl, DIAGS, v, None)
        log_call(self, "jeu_possible", ("L", fc, fl, "diags", v, None), J)

        self._apply_hover(None, [])

        captured = do_move(self.L, fc, fl, tc, tl, is_cap)

        cells_to_redraw = {(fc, fl), (tc, tl)}
        if captured:
            cells_to_redraw.add(captured)

        if self.L[tc][tl][1] == 1:
            if (self.current_player == 1 and tc == self.c - 1) or (
                self.current_player == 2 and tc == 0
            ):
                self.L[tc][tl][1] = 2
                self.append_log("Promotion en dame!")

        for c, l in cells_to_redraw:
            self._draw_cell(c, l)

        cap_txt = " (capture)" if is_cap else ""
        self.append_log(f"Déplacement: ({fc},{fl}) → ({tc},{tl}){cap_txt}")

        self._play_beep(is_cap)
        self._next_turn()

    # ── turn management ──

    def _next_turn(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self.label_tour.configure(
            text="Tour des Noirs" if self.current_player == 1 else "Tour des Blancs"
        )
        self._log_teams()
        r1 = team_exist(self.L, 1)
        r2 = team_exist(self.L, 2)
        if not r1:
            self.label_tour.configure(text="Les Blancs ont gagné!")
            self.append_log("=== Les Blancs ont gagné! ===")
            self._game_over = True
        elif not r2:
            self.label_tour.configure(text="Les Noirs ont gagné!")
            self.append_log("=== Les Noirs ont gagné! ===")
            self._game_over = True

    # ── sound ──

    def _play_beep(self, is_capture=False):
        """Son de feedback après un mouvement (non-bloquant)."""
        if not _HAS_WINSOUND:
            return
        freq = 800 if is_capture else BEEP_FREQ
        dur = BEEP_DURATION
        threading.Thread(target=winsound.Beep, args=(freq, dur), daemon=True).start()

    # ── log ──

    def append_log(self, msg: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _log_teams(self):
        r1 = team_exist(self.L, 1)
        r2 = team_exist(self.L, 2)
        log_call(self, "team_exist", ("L", 1), r1)
        log_call(self, "team_exist", ("L", 2), r2)


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = DameGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
