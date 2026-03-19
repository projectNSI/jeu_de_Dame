# -*- coding: utf-8 -*-
"""
Interface graphique du Jeu de Dames avec CustomTkinter.
Layout: gauche = plateau, droite haut = historique, droite bas = log.
Fonctionnalités: rafle, capture obligatoire, undo, sauvegarde/chargement,
minuterie, export historique, raccourcis clavier, thèmes.
"""

import sys
import os
import json
import copy
import time
import threading
from datetime import datetime
from tkinter import filedialog

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from damedemain import is_friendly, jeu_possible, team_exist

try:
    import winsound

    _HAS_WINSOUND = True
except ImportError:
    _HAS_WINSOUND = False

DIAGS = [[-1, 1], [1, 1], [-1, -1], [1, -1]]
SQUARE_SIZE = 68
PIECE_FONT = 44

DARK_SQ = "#8B4513"
LIGHT_SQ = "#DEB887"
HL_PIECE = "#4a7c59"
HL_MOVE = "#7FDB7F"
HL_LAST_FROM = "#b8a960"
HL_LAST_TO = "#c8b970"
HL_CHAIN = "#e08040"
CLR_NOIR = "#1E90FF"
CLR_BLANC = "#DC143C"

THEMES = {
    "Classique": {"dark": "#8B4513", "light": "#DEB887"},
    "Émeraude": {"dark": "#2d6a4f", "light": "#b7e4c7"},
    "Océan": {"dark": "#1b4965", "light": "#bee9e8"},
    "Crépuscule": {"dark": "#6d435a", "light": "#d4a5a5"},
}


def col_letter(c):
    return chr(ord("A") + c)


def cell_name(col, ligne):
    return f"{col_letter(col)}{ligne + 1}"


def log_call(gui, name, args, result):
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


def _has_captures(L, col, ligne, v):
    J = jeu_possible(L, col, ligne, DIAGS, v, None)
    if not J:
        return False
    if isinstance(J[0], list):
        return any(
            J[tc][tl] == 1 for tc in range(len(J)) for tl in range(len(J[0]))
        )
    return any(j == 1 for j in J)


def _any_capture_available(L, v, c_max, l_max):
    for col in range(c_max):
        for ligne in range(l_max):
            if is_friendly(L, col, ligne, v) and _has_captures(L, col, ligne, v):
                return True
    return False


# ═══════════════════════════════════════════════════════════════════
class DameGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Jeu de Dames")
        self.resizable(True, True)

        self._load_config()

        self.L = create_board(self.c, self.l, self.N)
        self.current_player = 1
        self.hover_piece = None
        self.hover_moves = []
        self._game_over = False
        self._clear_timer = None
        self.move_number = 0
        self.history_stack = []
        self._chain_piece = None
        self._chain_count = 0
        self._last_move = None
        self.score = {1: 0, 2: 0}
        self._turn_start = time.time()
        self._game_start = time.time()
        self._current_theme = "Classique"

        board_px = max(self.c, self.l) * SQUARE_SIZE
        self.geometry(f"{board_px + 560}x{board_px + 120}")
        try:
            self.state("zoomed")
        except Exception:
            pass

        self.bind("<Control-z>", lambda e: self._undo())
        self.bind("<Control-n>", lambda e: self._new_game())
        self.bind("<Control-s>", lambda e: self._save_game())
        self.bind("<Control-o>", lambda e: self._load_game())

        self._build_ui()
        self.append_log("=== Démarrage du jeu ===")
        self._log_teams()
        self._save_state()
        self._tick_timer()

    def _load_config(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(root_dir)
        for base in (project_root, root_dir, os.getcwd()):
            p = os.path.join(base, "config", "regle.json")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    cfg = json.load(f)[0]
                    self.c = cfg.get("colonne", 8)
                    self.l = cfg.get("ligne", 8)
                    self.N = cfg.get("ligne_de_pion", 3)
                return
        self.c, self.l, self.N = 8, 8, 3

    # ── UI construction ──

    def _build_ui(self):
        root_frame = ctk.CTkFrame(self, fg_color="transparent")
        root_frame.pack(fill="both", expand=True, padx=10, pady=10)
        root_frame.grid_columnconfigure(0, weight=0)
        root_frame.grid_columnconfigure(1, weight=1)
        root_frame.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(root_frame, fg_color="transparent")
        left.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        # top bar: turn + timer
        top_bar = ctk.CTkFrame(left, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 2))
        self.label_tour = ctk.CTkLabel(
            top_bar, text="Tour des Noirs (●)", font=("Arial", 20, "bold")
        )
        self.label_tour.pack(side="left")
        self.label_timer = ctk.CTkLabel(
            top_bar, text="⏱ 0:00", font=("Consolas", 15), text_color="#aaa"
        )
        self.label_timer.pack(side="right", padx=(10, 0))

        # score bar
        score_bar = ctk.CTkFrame(left, fg_color="transparent")
        score_bar.pack(fill="x", pady=(0, 4))
        self.label_score = ctk.CTkLabel(
            score_bar, text="Captures — Noir: 0  Blanc: 0",
            font=("Arial", 13), text_color="#ccc",
        )
        self.label_score.pack(side="left")

        # board
        board_outer = ctk.CTkFrame(left, fg_color="#2b2b2b", corner_radius=4)
        board_outer.pack()

        header = ctk.CTkFrame(board_outer, fg_color="transparent")
        header.pack(fill="x", padx=2)
        ctk.CTkLabel(header, text="", width=28).pack(side="left")
        for col in range(self.c):
            ctk.CTkLabel(
                header, text=col_letter(col), width=SQUARE_SIZE,
                font=("Consolas", 12, "bold"), text_color="#aaa",
            ).pack(side="left")

        board_body = ctk.CTkFrame(board_outer, fg_color="transparent")
        board_body.pack()

        self._board_frame = ctk.CTkFrame(
            board_body, fg_color="#2b2b2b", corner_radius=0
        )
        self._board_frame.pack(side="right")
        self._board_frame.bind("<Leave>", lambda e: self._schedule_clear())

        row_labels = ctk.CTkFrame(board_body, fg_color="transparent")
        row_labels.pack(side="left", fill="y")
        for ligne in range(self.l):
            ctk.CTkLabel(
                row_labels, text=str(ligne + 1), height=SQUARE_SIZE,
                width=28, font=("Consolas", 12, "bold"), text_color="#aaa",
            ).pack()

        self.squares = []
        for ligne in range(self.l):
            row = []
            for col in range(self.c):
                base = DARK_SQ if self.L[col][ligne][2] == 1 else LIGHT_SQ
                sq = ctk.CTkButton(
                    self._board_frame,
                    width=SQUARE_SIZE - 2, height=SQUARE_SIZE - 2,
                    text="", font=("Arial", PIECE_FONT),
                    fg_color=base, hover_color=base, text_color="#FFFFFF",
                    corner_radius=0,
                    command=lambda c=col, l=ligne: self._on_click(c, l),
                )
                sq.bind(
                    "<Enter>", lambda e, c=col, l=ligne: self._on_enter(c, l)
                )
                sq.grid(row=ligne, column=col, padx=0, pady=0)
                row.append(sq)
            self.squares.append(row)

        self._draw_all_pieces()

        # buttons row 1
        btn1 = ctk.CTkFrame(left, fg_color="transparent")
        btn1.pack(pady=(6, 0), fill="x")
        ctk.CTkButton(
            btn1, text="⟲ Annuler (Ctrl+Z)", font=("Arial", 13),
            width=155, height=30, command=self._undo,
        ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(
            btn1, text="⟳ Nouvelle partie (Ctrl+N)", font=("Arial", 13),
            width=190, height=30, command=self._new_game, fg_color="#555",
        ).pack(side="left")

        # buttons row 2
        btn2 = ctk.CTkFrame(left, fg_color="transparent")
        btn2.pack(pady=(4, 0), fill="x")
        ctk.CTkButton(
            btn2, text="💾 Sauvegarder (Ctrl+S)", font=("Arial", 13),
            width=170, height=30, command=self._save_game, fg_color="#3a6b35",
        ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(
            btn2, text="📂 Charger (Ctrl+O)", font=("Arial", 13),
            width=150, height=30, command=self._load_game, fg_color="#3a6b35",
        ).pack(side="left")

        # theme selector
        theme_row = ctk.CTkFrame(left, fg_color="transparent")
        theme_row.pack(pady=(4, 0), fill="x")
        ctk.CTkLabel(theme_row, text="Thème:", font=("Arial", 12)).pack(side="left")
        self.theme_menu = ctk.CTkOptionMenu(
            theme_row, values=list(THEMES.keys()),
            command=self._change_theme, font=("Arial", 12),
            width=130, height=26,
        )
        self.theme_menu.set(self._current_theme)
        self.theme_menu.pack(side="left", padx=(4, 0))

        # RIGHT panels
        right = ctk.CTkFrame(root_frame, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # history
        hist_frame = ctk.CTkFrame(right, fg_color="#1e1e1e", corner_radius=6)
        hist_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 6))
        hist_header = ctk.CTkFrame(hist_frame, fg_color="transparent")
        hist_header.pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(
            hist_header, text="Historique des coups",
            font=("Arial", 16, "bold"),
        ).pack(side="left")
        ctk.CTkButton(
            hist_header, text="📋 Exporter", font=("Arial", 11),
            width=90, height=24, command=self._export_history, fg_color="#555",
        ).pack(side="right")
        self.hist_text = ctk.CTkTextbox(
            hist_frame, font=("Consolas", 14), state="disabled"
        )
        self.hist_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # log
        log_frame = ctk.CTkFrame(right, fg_color="#1a1a1a", corner_radius=6)
        log_frame.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(
            log_frame, text="Journal des appels (log)",
            font=("Arial", 16, "bold"),
        ).pack(anchor="w", padx=12, pady=(8, 2))
        self.log_text = ctk.CTkTextbox(
            log_frame, font=("Consolas", 13), state="disabled"
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ── rendering ──

    def _base_color(self, col, ligne):
        return DARK_SQ if self.L[col][ligne][2] == 1 else LIGHT_SQ

    def _piece_txt(self, col, ligne):
        p = self.L[col][ligne]
        if p[0] == 1:
            return ("♔" if p[1] == 2 else "●", CLR_NOIR)
        if p[0] == 2:
            return ("♕" if p[1] == 2 else "●", CLR_BLANC)
        return ("", "#FFFFFF")

    def _last_move_bg(self, col, ligne):
        if self._last_move:
            if (col, ligne) == self._last_move[0]:
                return HL_LAST_FROM
            if (col, ligne) == self._last_move[1]:
                return HL_LAST_TO
        return None

    def _set_bg(self, col, ligne, bg=None):
        if bg is None:
            bg = self._last_move_bg(col, ligne) or self._base_color(col, ligne)
        self.squares[ligne][col].configure(fg_color=bg, hover_color=bg)

    def _draw_cell(self, col, ligne, bg=None):
        self._set_bg(col, ligne, bg)
        txt, tc = self._piece_txt(col, ligne)
        self.squares[ligne][col].configure(text=txt, text_color=tc)

    def _draw_all_pieces(self):
        for col in range(self.c):
            for ligne in range(self.l):
                self._draw_cell(col, ligne)

    def _update_score_label(self):
        self.label_score.configure(
            text=f"Captures — Noir: {self.score[1]}  Blanc: {self.score[2]}"
        )

    # ── hover ──

    def _apply_hover(self, piece, moves):
        old = set()
        if self.hover_piece:
            old.add(self.hover_piece)
        for m in self.hover_moves:
            old.add((m[0], m[1]))
        new_map = {}
        if piece:
            new_map[piece] = HL_CHAIN if self._chain_piece else HL_PIECE
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
        if self._clear_timer:
            self.after_cancel(self._clear_timer)
        self._clear_timer = self.after(60, self._do_scheduled_clear)

    def _do_scheduled_clear(self):
        self._clear_timer = None
        if not self._chain_piece:
            self._clear_hover()

    def _cancel_clear(self):
        if self._clear_timer:
            self.after_cancel(self._clear_timer)
            self._clear_timer = None

    def _on_enter(self, col, ligne):
        self._cancel_clear()
        if self._game_over:
            return

        if self._chain_piece:
            # during chain capture, ignore hover on other cells
            return

        dests = {(m[0], m[1]) for m in self.hover_moves}
        if (col, ligne) in dests or (col, ligne) == self.hover_piece:
            return

        v = 1 if self.current_player == 1 else 0
        if not is_friendly(self.L, col, ligne, v):
            return

        J = jeu_possible(self.L, col, ligne, DIAGS, v, None)
        moves = get_moves(self.L, col, ligne, J, v)

        if _any_capture_available(self.L, v, self.c, self.l):
            moves = [m for m in moves if m[2]]
            if not moves:
                return
        self._apply_hover((col, ligne), moves)

    # ── click ──

    def _on_click(self, col, ligne):
        if self._game_over:
            return
        dest = next(
            (m for m in self.hover_moves if m[0] == col and m[1] == ligne), None
        )
        if not dest or not self.hover_piece:
            return

        if not self._chain_piece:
            self._save_state()

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
            self.score[self.current_player] += 1
            self._update_score_label()

        promoted = False
        if self.L[tc][tl][1] == 1:
            if (self.current_player == 1 and tc == self.c - 1) or (
                self.current_player == 2 and tc == 0
            ):
                self.L[tc][tl][1] = 2
                promoted = True
                self.append_log("Promotion en dame!")

        self._last_move = ((fc, fl), (tc, tl))
        for cr, lr in cells_to_redraw:
            self._draw_cell(cr, lr)

        self.move_number += 1
        if is_cap:
            self._chain_count += 1
        self._add_history(fc, fl, tc, tl, is_cap, captured, promoted)

        # ── rafle: chain capture check ──
        if is_cap and not promoted and _has_captures(self.L, tc, tl, v):
            self._chain_piece = (tc, tl)
            J2 = jeu_possible(self.L, tc, tl, DIAGS, v, None)
            chain_moves = [m for m in get_moves(self.L, tc, tl, J2, v) if m[2]]
            self._apply_hover((tc, tl), chain_moves)
            self.append_log(
                f"Rafle! Capture en chaîne depuis {cell_name(tc, tl)}"
            )
            self._play_sound(True, False)
            return

        self._chain_piece = None
        self._chain_count = 0
        self._play_sound(is_cap, promoted)
        self._next_turn()

    # ── history ──

    def _add_history(self, fc, fl, tc, tl, is_cap, captured, promoted):
        player = "Noir" if self.current_player == 1 else "Blanc"
        piece = self.L[tc][tl]
        kind = "Dame" if piece[1] == 2 and not promoted else "Pion"
        src, dst = cell_name(fc, fl), cell_name(tc, tl)
        chain_tag = (
            f" [rafle ×{self._chain_count}]"
            if self._chain_piece and self._chain_count > 1
            else ""
        )
        parts = [f"#{self.move_number:>3}  {player:<6} {kind:<5} {src} → {dst}"]
        if is_cap and captured:
            parts.append(f"  ✕ capture en {cell_name(*captured)}")
        if promoted:
            parts.append("  ★ promu en Dame")
        if chain_tag:
            parts.append(chain_tag)
        line = "".join(parts)
        self.hist_text.configure(state="normal")
        self.hist_text.insert("end", line + "\n")
        self.hist_text.see("end")
        self.hist_text.configure(state="disabled")

    # ── undo ──

    def _save_state(self):
        hist = ""
        if hasattr(self, "hist_text"):
            self.hist_text.configure(state="normal")
            hist = self.hist_text.get("1.0", "end-1c")
            self.hist_text.configure(state="disabled")
        self.history_stack.append((
            copy.deepcopy(self.L),
            self.current_player,
            self.move_number,
            copy.deepcopy(self.score),
            self._last_move,
            hist,
        ))

    def _undo(self):
        if len(self.history_stack) <= 1:
            return
        if self._chain_piece:
            self._chain_piece = None
            self._chain_count = 0
        self.history_stack.pop()
        L_cp, player, mv, score, last, hist = self.history_stack[-1]
        self.L = copy.deepcopy(L_cp)
        self.current_player = player
        self.move_number = mv
        self.score = copy.deepcopy(score)
        self._last_move = last
        self._game_over = False
        self.hover_piece = None
        self.hover_moves = []
        self._draw_all_pieces()
        self._update_score_label()
        self.label_tour.configure(
            text="Tour des Noirs (●)"
            if self.current_player == 1
            else "Tour des Blancs (●)"
        )
        self.hist_text.configure(state="normal")
        self.hist_text.delete("1.0", "end")
        if hist:
            self.hist_text.insert("1.0", hist)
        self.hist_text.see("end")
        self.hist_text.configure(state="disabled")
        self.append_log(f"← Annulation du coup #{mv + 1}")
        self._turn_start = time.time()
        self._play_undo_sound()

    # ── new game ──

    def _new_game(self):
        self.L = create_board(self.c, self.l, self.N)
        self.current_player = 1
        self.hover_piece = None
        self.hover_moves = []
        self._game_over = False
        self.move_number = 0
        self.history_stack = []
        self._chain_piece = None
        self._chain_count = 0
        self._last_move = None
        self.score = {1: 0, 2: 0}
        self._turn_start = time.time()
        self._game_start = time.time()
        self._draw_all_pieces()
        self._update_score_label()
        self.label_tour.configure(text="Tour des Noirs (●)")
        self.hist_text.configure(state="normal")
        self.hist_text.delete("1.0", "end")
        self.hist_text.configure(state="disabled")
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.append_log("=== Nouvelle partie ===")
        self._log_teams()
        self._save_state()

    # ── save / load ──

    def _save_game(self):
        path = filedialog.asksaveasfilename(
            title="Sauvegarder la partie",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not path:
            return
        self.hist_text.configure(state="normal")
        hist = self.hist_text.get("1.0", "end-1c")
        self.hist_text.configure(state="disabled")
        data = {
            "board": self.L,
            "player": self.current_player,
            "move_number": self.move_number,
            "score": self.score,
            "c": self.c,
            "l": self.l,
            "N": self.N,
            "history_text": hist,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.append_log(f"Partie sauvegardée → {os.path.basename(path)}")

    def _load_game(self):
        path = filedialog.askopenfilename(
            title="Charger une partie",
            filetypes=[("JSON", "*.json")],
        )
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.L = data["board"]
        self.current_player = data["player"]
        self.move_number = data["move_number"]
        self.score = {int(k): v for k, v in data["score"].items()}
        self._game_over = False
        self._chain_piece = None
        self._chain_count = 0
        self._last_move = None
        self.hover_piece = None
        self.hover_moves = []
        self.history_stack = []
        self._turn_start = time.time()
        self._game_start = time.time()
        self._draw_all_pieces()
        self._update_score_label()
        self.label_tour.configure(
            text="Tour des Noirs (●)"
            if self.current_player == 1
            else "Tour des Blancs (●)"
        )
        hist = data.get("history_text", "")
        self.hist_text.configure(state="normal")
        self.hist_text.delete("1.0", "end")
        if hist:
            self.hist_text.insert("1.0", hist)
        self.hist_text.configure(state="disabled")
        self.append_log(f"Partie chargée ← {os.path.basename(path)}")
        self._save_state()

    # ── export history ──

    def _export_history(self):
        path = filedialog.asksaveasfilename(
            title="Exporter l'historique",
            defaultextension=".txt",
            filetypes=[("Texte", "*.txt")],
        )
        if not path:
            return
        self.hist_text.configure(state="normal")
        content = self.hist_text.get("1.0", "end-1c")
        self.hist_text.configure(state="disabled")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Jeu de Dames — Historique des coups\n")
            f.write(f"Exporté le {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(content + "\n")
        self.append_log(f"Historique exporté → {os.path.basename(path)}")

    # ── theme ──

    def _change_theme(self, name):
        global DARK_SQ, LIGHT_SQ
        if name not in THEMES:
            return
        self._current_theme = name
        t = THEMES[name]
        DARK_SQ = t["dark"]
        LIGHT_SQ = t["light"]
        self._draw_all_pieces()

    # ── turn ──

    def _next_turn(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self._turn_start = time.time()
        self.label_tour.configure(
            text="Tour des Noirs (●)"
            if self.current_player == 1
            else "Tour des Blancs (●)"
        )
        self._log_teams()
        r1 = team_exist(self.L, 1)
        r2 = team_exist(self.L, 2)
        if not r1:
            self.label_tour.configure(text="Les Blancs ont gagné!")
            self.append_log("=== Les Blancs ont gagné! ===")
            self._game_over = True
            self._play_victory_sound()
        elif not r2:
            self.label_tour.configure(text="Les Noirs ont gagné!")
            self.append_log("=== Les Noirs ont gagné! ===")
            self._game_over = True
            self._play_victory_sound()

    # ── timer ──

    def _tick_timer(self):
        if not self._game_over:
            elapsed = int(time.time() - self._turn_start)
            m, s = divmod(elapsed, 60)
            total = int(time.time() - self._game_start)
            tm, ts = divmod(total, 60)
            self.label_timer.configure(
                text=f"⏱ {m}:{s:02d}  (total {tm}:{ts:02d})"
            )
        self.after(1000, self._tick_timer)

    # ── sound ──

    def _beep_seq(self, notes):
        if not _HAS_WINSOUND:
            return
        def _play():
            for freq, dur in notes:
                winsound.Beep(freq, dur)
        threading.Thread(target=_play, daemon=True).start()

    def _play_sound(self, is_capture=False, is_promotion=False):
        if is_promotion:
            self._beep_seq([(880, 100), (1100, 100), (1320, 150)])
        elif is_capture:
            self._beep_seq([(700, 80), (900, 120)])
        else:
            self._beep_seq([(660, 120)])

    def _play_undo_sound(self):
        self._beep_seq([(500, 80), (400, 120)])

    def _play_victory_sound(self):
        self._beep_seq([(880, 120), (1100, 120), (1320, 120), (1760, 250)])

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
