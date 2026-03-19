# -*- coding: utf-8 -*-
"""
Jeu de Dames — Interface Pygame (compatible Pygbag pour le web).
Fonctionnalités: IA (3 niveaux), rafle, capture obligatoire,
undo, indice, minuterie, thèmes, historique des coups.
"""

import sys, os, math, time, random, copy, asyncio, json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from pygame import gfxdraw

from damedemain import is_friendly, jeu_possible, team_exist

# ═══════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════

def _load_game_config():
    c, l, n = 8, 8, 3
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(root_dir)
        cfg_path = os.path.join(project_root, "config", "regle.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)[0]
                c = int(data.get("colonne", 8))
                l = int(data.get("ligne", 8))
                n = int(data.get("ligne_de_pion", 3))
    except Exception:
        pass
    return c, l, n


COLS, ROWS, N_PAWN_ROWS = _load_game_config()
SQ = 68
FPS = 60

DIAGS = [[-1, 1], [1, 1], [-1, -1], [1, -1]]

THEMES = {
    "Classique":  {"dark": (139, 69, 19),  "light": (222, 184, 135)},
    "Émeraude":   {"dark": (45, 106, 79),  "light": (183, 228, 199)},
    "Océan":      {"dark": (27, 73, 101),  "light": (190, 233, 232)},
    "Crépuscule": {"dark": (109, 67, 90),  "light": (212, 165, 165)},
}
THEME_NAMES = list(THEMES.keys())

BG       = (18, 18, 18)
PANEL_BG = (26, 26, 26)
TEXT_CLR  = (224, 224, 224)
DIM_CLR  = (160, 160, 160)
GOLD     = (224, 200, 120)

HL_PIECE     = (74, 124, 89)
HL_MOVE      = (127, 219, 127)
HL_LAST_FROM = (184, 169, 96)
HL_LAST_TO   = (200, 185, 112)
HL_CHAIN     = (224, 128, 64)
HL_HINT      = (212, 160, 23)

CLR_NOIR  = (17, 17, 17)
CLR_BLANC = (240, 240, 240)

AI_LABELS = ["2 Joueurs", "IA Facile", "IA Moyen", "IA Difficile"]
AI_MAP    = {0: None, 1: "facile", 2: "moyen", 3: "difficile"}

# ═══════════════════════════════════════════
# GAME LOGIC (mirrors dame_gui_ctk helpers)
# ═══════════════════════════════════════════

def col_letter(c): return chr(ord("A") + c)
def cell_name(c, l): return f"{col_letter(c)}{l+1}"

def _copy_board(L):
    return [[[cell[0], cell[1], cell[2]] for cell in col] for col in L]

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
    piece = L[fc][fl][:]
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
            sc += dc; sl += dl
    L[tc][tl][0], L[tc][tl][1] = piece[0], piece[1]
    return captured

def _has_captures(L, col, ligne, v):
    J = jeu_possible(L, col, ligne, DIAGS, v, None)
    if not J: return False
    if isinstance(J[0], list):
        return any(J[tc][tl] == 1 for tc in range(len(J)) for tl in range(len(J[0])))
    return any(j == 1 for j in J)

def _any_capture_available(L, v, c, l):
    for col in range(c):
        for ligne in range(l):
            if is_friendly(L, col, ligne, v) and _has_captures(L, col, ligne, v):
                return True
    return False

def _get_all_moves(L, v, c, l):
    moves = []
    must_cap = _any_capture_available(L, v, c, l)
    for col in range(c):
        for ligne in range(l):
            if is_friendly(L, col, ligne, v):
                J = jeu_possible(L, col, ligne, DIAGS, v, None)
                mv = get_moves(L, col, ligne, J, v)
                if must_cap:
                    mv = [m for m in mv if m[2]]
                for m in mv:
                    moves.append((col, ligne, m[0], m[1], m[2]))
    return moves

def _sim_move(L, move, c):
    fc, fl, tc, tl, is_cap = move
    do_move(L, fc, fl, tc, tl, is_cap)
    if L[tc][tl][1] == 1:
        color = L[tc][tl][0]
        if (color == 1 and tc == c - 1) or (color == 2 and tc == 0):
            L[tc][tl][1] = 2

# ═══════════════════════════════════════════
# AI
# ═══════════════════════════════════════════

class SimpleAI:
    def __init__(self, difficulty, c, l):
        self.difficulty = difficulty
        self.c, self.l = c, l

    def choose_move(self, L, v):
        moves = _get_all_moves(L, v, self.c, self.l)
        if not moves: return None
        if self.difficulty == "facile": return random.choice(moves)
        if self.difficulty == "moyen": return self._greedy(L, v, moves)
        return self._minimax_root(L, v, moves)

    def _greedy(self, L, v, moves):
        scored = []
        for m in moves:
            Lc = _copy_board(L); _sim_move(Lc, m, self.c)
            scored.append((self._evaluate(Lc, v), m))
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][0]
        top = [s for s in scored if s[0] == best]
        return random.choice(top)[1]

    def _minimax_root(self, L, v, moves):
        best_score, best_moves = float("-inf"), []
        for m in moves:
            Lc = _copy_board(L); _sim_move(Lc, m, self.c)
            s = self._minimax(Lc, 2, False, v, float("-inf"), float("inf"))
            if s > best_score: best_score, best_moves = s, [m]
            elif s == best_score: best_moves.append(m)
        return random.choice(best_moves) if best_moves else moves[0]

    def _minimax(self, L, depth, maximizing, ai_v, alpha, beta):
        if depth == 0: return self._evaluate(L, ai_v)
        v = ai_v if maximizing else (1 - ai_v)
        moves = _get_all_moves(L, v, self.c, self.l)
        if not moves: return -999 if maximizing else 999
        if maximizing:
            val = float("-inf")
            for m in moves:
                Lc = _copy_board(L); _sim_move(Lc, m, self.c)
                val = max(val, self._minimax(Lc, depth-1, False, ai_v, alpha, beta))
                alpha = max(alpha, val)
                if beta <= alpha: break
            return val
        val = float("inf")
        for m in moves:
            Lc = _copy_board(L); _sim_move(Lc, m, self.c)
            val = min(val, self._minimax(Lc, depth-1, True, ai_v, alpha, beta))
            beta = min(beta, val)
            if beta <= alpha: break
        return val

    def _evaluate(self, L, ai_v):
        score = 0
        for col in range(self.c):
            for ligne in range(self.l):
                p = L[col][ligne]
                if p[0] == 0: continue
                val = 5.0 if p[1] == 2 else 1.0
                if p[1] == 1:
                    val += (col if p[0] == 1 else (self.c - 1 - col)) * 0.15
                p_v = 1 if p[0] == 1 else 0
                score += val if p_v == ai_v else -val
        return score

# ═══════════════════════════════════════════
# SOUND (pygame.mixer, Pygbag compatible)
# ═══════════════════════════════════════════

_sounds = {}

def _gen_tone(freq, dur_ms, vol=0.25):
    sr = 22050
    n = int(sr * dur_ms / 1000)
    import array as _arr
    buf = _arr.array("h", [0] * n)
    for i in range(n):
        t = i / sr
        fade = min(1.0, min(i, n - i) / (sr * 0.005 + 1))
        buf[i] = int(32767 * vol * fade * math.sin(2 * math.pi * freq * t))
    return pygame.mixer.Sound(buffer=buf)

class _SoundPlayer:
    def __init__(self):
        self.enabled = True
        self._queue = []

    def play_seq(self, notes):
        if not self.enabled:
            return
        t = time.time()
        for freq, dur in notes:
            key = (freq, dur)
            if key not in _sounds:
                _sounds[key] = _gen_tone(freq, dur)
            self._queue.append((t, key))
            t += dur / 1000.0

    def update(self):
        if not self.enabled:
            return
        now = time.time()
        if not self._queue:
            return
        remain = []
        for at, key in self._queue:
            if at <= now:
                _sounds[key].play()
            else:
                remain.append((at, key))
        self._queue = remain


SOUND = _SoundPlayer()

def snd_move():    SOUND.play_seq([(500, 80), (1000, 80)])
def snd_capture(): SOUND.play_seq([(1400, 70), (350, 130)])
def snd_promote(): SOUND.play_seq([(440, 60), (660, 60), (880, 60), (1100, 60), (1400, 100)])
def snd_undo():    SOUND.play_seq([(900, 60), (300, 100)])
def snd_victory(): SOUND.play_seq([(523, 80), (659, 80), (784, 80), (1047, 80), (1319, 80), (1568, 160)])

# ═══════════════════════════════════════════
# DRAWING HELPERS
# ═══════════════════════════════════════════

def draw_aa_circle(surf, color, center, radius):
    x, y = int(center[0]), int(center[1])
    r = int(radius)
    try:
        gfxdraw.aacircle(surf, x, y, r, color)
        gfxdraw.filled_circle(surf, x, y, r, color)
    except Exception:
        pygame.draw.circle(surf, color, center, radius)

def draw_text(surf, text, pos, font, color=TEXT_CLR, anchor="topleft"):
    ts = font.render(text, True, color)
    r = ts.get_rect(**{anchor: pos})
    surf.blit(ts, r)
    return r

def draw_btn(surf, rect, text, font, base_col=(45, 106, 79), hover=False):
    c = tuple(min(255, v + 30) for v in base_col) if hover else base_col
    pygame.draw.rect(surf, c, rect, border_radius=6)
    draw_text(surf, text, rect.center, font, TEXT_CLR, "center")

# ═══════════════════════════════════════════
# SCROLLABLE LOG
# ═══════════════════════════════════════════

class LogPanel:
    def __init__(self, rect, font, title=""):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.title = title
        self.lines = []
        self.scroll = 0

    def append(self, text):
        self.lines.append(text)
        self.scroll = max(0, len(self.lines) - self._visible_lines())

    def clear(self):
        self.lines.clear()
        self.scroll = 0

    def set_lines(self, lines):
        self.lines = list(lines)
        self.scroll = max(0, len(self.lines) - self._visible_lines())

    def _visible_lines(self):
        h = self.rect.h - (30 if self.title else 8) - 8
        return max(1, h // (self.font.get_height() + 2))

    def handle_scroll(self, dy):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            max_scroll = max(0, len(self.lines) - self._visible_lines())
            self.scroll = max(0, min(self.scroll - dy, max_scroll))

    def draw(self, surf):
        pygame.draw.rect(surf, PANEL_BG, self.rect, border_radius=6)
        y = self.rect.y + 4
        if self.title:
            draw_text(surf, self.title, (self.rect.x + 10, y), self.font, DIM_CLR)
            y += 24
        vis = self._visible_lines()
        start = max(0, self.scroll)
        clip = pygame.Rect(self.rect.x, y, self.rect.w, self.rect.h - (y - self.rect.y) - 4)
        surf.set_clip(clip)
        for i in range(start, min(start + vis + 1, len(self.lines))):
            draw_text(surf, self.lines[i], (self.rect.x + 8, y), self.font, TEXT_CLR)
            y += self.font.get_height() + 2
        surf.set_clip(None)

# ═══════════════════════════════════════════
# GAME CLASS
# ═══════════════════════════════════════════

class DameGame:
    def __init__(self, screen, ai_mode=None, theme_idx=0):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.c = self.l = COLS

        self.font_sm = pygame.font.SysFont("consolas,courier", 13)
        self.font_md = pygame.font.SysFont("segoeui,arial", 16)
        self.font_lg = pygame.font.SysFont("segoeui,arial", 22, bold=True)
        self.font_piece = pygame.font.SysFont("segoeui,arial", int(SQ * 0.55), bold=True)
        self.font_coord = pygame.font.SysFont("consolas,courier", 12, bold=True)

        self._compute_layout()
        self.hist_panel = LogPanel(self._hist_rect, self.font_sm, "Historique des coups")
        self.log_panel  = LogPanel(self._log_rect, self.font_sm, "Journal des appels")

        self._theme_idx = theme_idx
        self._apply_theme()
        self._ai_mode_idx = 0
        for k, v in AI_MAP.items():
            if v == ai_mode:
                self._ai_mode_idx = k
        self._ai_mode = ai_mode
        self.ai = SimpleAI(ai_mode, self.c, self.l) if ai_mode else None

        self._init_state()
        self._build_buttons()
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._project_root = os.path.dirname(root_dir)
        self._save_dir = os.path.join(self._project_root, "saves")
        self._export_dir = os.path.join(self._project_root, "exports")
        os.makedirs(self._save_dir, exist_ok=True)
        os.makedirs(self._export_dir, exist_ok=True)
        self._save_path = os.path.join(self._save_dir, "savegame_pygame.json")
        self.log_panel.append("=== Démarrage du jeu ===")
        if self._ai_mode:
            self.log_panel.append(f"Mode IA: {self._ai_mode}")

    def _compute_layout(self):
        self.W, self.H = self.screen.get_size()
        self.board_x = 30
        self.board_y = 60
        panel_x = self.board_x + COLS * SQ + 50
        panel_w = max(260, self.W - panel_x - 16)
        half_h = max(180, (self.H - 80) // 2 - 6)
        self._hist_rect = (panel_x, 10, panel_w, half_h)
        self._log_rect = (panel_x, 10 + half_h + 12, panel_w, half_h)

    def set_screen(self, screen):
        self.screen = screen
        self._compute_layout()
        self.hist_panel.rect = pygame.Rect(self._hist_rect)
        self.log_panel.rect = pygame.Rect(self._log_rect)
        self._build_buttons()

    def _init_state(self):
        self.L = create_board(self.c, self.l, N_PAWN_ROWS)
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
        self._flash_cells = {}
        self._ai_pending = None
        self._hint = None
        self._hint_expire = 0
        self._save_state()

    def _apply_theme(self):
        t = THEMES[THEME_NAMES[self._theme_idx]]
        self.dark_sq = t["dark"]
        self.light_sq = t["light"]

    def _build_buttons(self):
        bx = self.board_x
        by = self.board_y + ROWS * SQ + 12
        bw, bh, gap = 120, 30, 6
        self.buttons = [
            (pygame.Rect(bx, by, bw, bh), "⟲ Annuler", self.undo, (45, 106, 79)),
            (pygame.Rect(bx + bw + gap, by, bw, bh), "💡 Indice", self.show_hint, (122, 101, 32)),
            (pygame.Rect(bx + 2*(bw+gap), by, bw, bh), "⟳ Nouvelle", self.new_game, (85, 85, 85)),
            (pygame.Rect(bx + 3*(bw+gap), by, 90, bh), "🏠 Menu", "__MENU__", (85, 85, 85)),
        ]
        by2 = by + bh + 6
        self.buttons += [
            (pygame.Rect(bx, by2, bw, bh), "💾 Save", self.save_game, (58, 107, 53)),
            (pygame.Rect(bx + bw + gap, by2, bw, bh), "📂 Load", self.load_game, (58, 107, 53)),
            (pygame.Rect(bx + 2*(bw+gap), by2, bw, bh), "📋 Export", self.export_history, (85, 85, 85)),
        ]
        # Theme / AI selectors (rendered as clickable labels)
        self._theme_rect = pygame.Rect(bx, by2 + bh + 8, 200, 24)
        self._ai_rect = pygame.Rect(bx + 210, by2 + bh + 8, 200, 24)

    # ── state ──

    def _save_state(self):
        self.history_stack.append((
            copy.deepcopy(self.L), self.current_player,
            self.move_number, copy.deepcopy(self.score),
            self._last_move, list(self.hist_panel.lines),
        ))

    # ── board position helpers ──

    def _cell_rect(self, col, ligne):
        return pygame.Rect(self.board_x + col * SQ, self.board_y + ligne * SQ, SQ, SQ)

    def _mouse_cell(self, pos):
        x, y = pos
        col = (x - self.board_x) // SQ
        ligne = (y - self.board_y) // SQ
        if 0 <= col < COLS and 0 <= ligne < ROWS:
            return col, ligne
        return None, None

    def _cell_color(self, col, ligne):
        return self.dark_sq if self.L[col][ligne][2] == 1 else self.light_sq

    def _bg_for(self, col, ligne):
        if self._hint and time.time() < self._hint_expire:
            if (col, ligne) in self._hint:
                return HL_HINT
        if self._last_move:
            if (col, ligne) == self._last_move[0]: return HL_LAST_FROM
            if (col, ligne) == self._last_move[1]: return HL_LAST_TO
        return self._cell_color(col, ligne)

    # ── AI helpers ──

    def _is_ai_turn(self):
        return self._ai_mode and self.current_player == 2 and not self._game_over

    # ── hover ──

    def _update_hover(self, mx, my):
        if self._game_over or self._is_ai_turn() or self._chain_piece:
            return
        col, ligne = self._mouse_cell((mx, my))
        if col is None:
            self.hover_piece = None
            self.hover_moves = []
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
        self.hover_piece = (col, ligne)
        self.hover_moves = moves

    # ── move execution ──

    def _execute_move(self, fc, fl, tc, tl, is_cap):
        if not self._chain_piece:
            self._save_state()

        v = 1 if self.current_player == 1 else 0
        self.log_panel.append(f"→ is_friendly(L,{fc},{fl},{v}) = True")
        J = jeu_possible(self.L, fc, fl, DIAGS, v, None)
        self.log_panel.append(f"→ jeu_possible(L,{fc},{fl},diags,{v}) = ...")

        self.hover_piece = None
        self.hover_moves = []

        captured = do_move(self.L, fc, fl, tc, tl, is_cap)

        if captured:
            self.score[self.current_player] += 1
            self._flash_cells[captured] = time.time()

        promoted = False
        if self.L[tc][tl][1] == 1:
            if (self.current_player == 1 and tc == self.c - 1) or \
               (self.current_player == 2 and tc == 0):
                self.L[tc][tl][1] = 2
                promoted = True
                self.log_panel.append("Promotion en dame!")

        self._last_move = ((fc, fl), (tc, tl))
        self.move_number += 1
        if is_cap:
            self._chain_count += 1

        self._add_history(fc, fl, tc, tl, is_cap, captured, promoted)

        if is_cap and not promoted and _has_captures(self.L, tc, tl, v):
            self._chain_piece = (tc, tl)
            J2 = jeu_possible(self.L, tc, tl, DIAGS, v, None)
            chain_moves = [m for m in get_moves(self.L, tc, tl, J2, v) if m[2]]
            self.hover_piece = (tc, tl)
            self.hover_moves = chain_moves
            self.log_panel.append(f"Rafle! depuis {cell_name(tc,tl)}")
            try: snd_capture()
            except: pass
            return True

        self._chain_piece = None
        self._chain_count = 0
        try:
            if promoted: snd_promote()
            elif is_cap: snd_capture()
            else: snd_move()
        except: pass
        self._next_turn()
        return False

    def _add_history(self, fc, fl, tc, tl, is_cap, captured, promoted):
        player = "Noir" if self.current_player == 1 else "Blanc"
        kind = "Dame" if self.L[tc][tl][1] == 2 and not promoted else "Pion"
        line = f"#{self.move_number:>3} {player:<6} {kind:<5} {cell_name(fc,fl)} → {cell_name(tc,tl)}"
        if is_cap and captured:
            line += f"  ✕{cell_name(*captured)}"
        if promoted:
            line += "  ★Dame"
        if self._chain_piece and self._chain_count > 1:
            line += f" [rafle ×{self._chain_count}]"
        self.hist_panel.append(line)

    def _next_turn(self):
        self.current_player = 2 if self.current_player == 1 else 1
        self._turn_start = time.time()
        r1 = team_exist(self.L, 1)
        r2 = team_exist(self.L, 2)
        self.log_panel.append(f"→ team_exist(L,1) = {r1}")
        self.log_panel.append(f"→ team_exist(L,2) = {r2}")
        v = 1 if self.current_player == 1 else 0
        no_moves = not _get_all_moves(self.L, v, self.c, self.l)
        if not r1 or (self.current_player == 1 and no_moves):
            self._game_over = True
            self.log_panel.append("=== Les Blancs ont gagné! ===")
            try: snd_victory()
            except: pass
        elif not r2 or (self.current_player == 2 and no_moves):
            self._game_over = True
            self.log_panel.append("=== Les Noirs ont gagné! ===")
            try: snd_victory()
            except: pass
        elif self._is_ai_turn():
            self._ai_pending = time.time() + 0.5

    # ── click ──

    def handle_click(self, pos):
        for rect, label, action, _ in self.buttons:
            if rect.collidepoint(pos):
                if action == "__MENU__":
                    return "__MENU__"
                if callable(action):
                    action()
                return "__NONE__"

        if self._game_over or self._is_ai_turn():
            return "__NONE__"

        if self._theme_rect.collidepoint(pos):
            self._theme_idx = (self._theme_idx + 1) % len(THEME_NAMES)
            self._apply_theme()
            return "__NONE__"
        if self._ai_rect.collidepoint(pos):
            self._ai_mode_idx = (self._ai_mode_idx + 1) % len(AI_LABELS)
            self._ai_mode = AI_MAP[self._ai_mode_idx]
            self.ai = SimpleAI(self._ai_mode, self.c, self.l) if self._ai_mode else None
            self.log_panel.append(f"Mode: {AI_LABELS[self._ai_mode_idx]}")
            if self._is_ai_turn():
                self._ai_pending = time.time() + 0.4
            return "__NONE__"

        col, ligne = self._mouse_cell(pos)
        if col is None:
            return "__NONE__"

        dest = next((m for m in self.hover_moves if m[0] == col and m[1] == ligne), None)
        if not dest or not self.hover_piece:
            return "__NONE__"
        fc, fl = self.hover_piece
        tc, tl, is_cap = dest
        self._execute_move(fc, fl, tc, tl, is_cap)
        return "__NONE__"

    # ── AI ──

    def update_ai(self):
        if self._ai_pending and time.time() >= self._ai_pending:
            self._ai_pending = None
            if self._chain_piece:
                self._ai_chain_step()
            else:
                self._ai_move()

    def _ai_move(self):
        if not self._is_ai_turn(): return
        v = 0
        move = self.ai.choose_move(self.L, v)
        if not move:
            self._game_over = True
            self.log_panel.append("=== IA bloquée. Les Noirs ont gagné! ===")
            try: snd_victory()
            except: pass
            return
        fc, fl, tc, tl, is_cap = move
        self.log_panel.append(f"🤖 IA: {cell_name(fc,fl)} → {cell_name(tc,tl)}")
        chain = self._execute_move(fc, fl, tc, tl, is_cap)
        if chain:
            self._ai_pending = time.time() + 0.45

    def _ai_chain_step(self):
        if not self._chain_piece or self._game_over: return
        col, ligne = self._chain_piece
        v = 0
        J = jeu_possible(self.L, col, ligne, DIAGS, v, None)
        caps = [m for m in get_moves(self.L, col, ligne, J, v) if m[2]]
        if not caps:
            self._chain_piece = None; self._chain_count = 0
            self._next_turn(); return
        if self._ai_mode == "difficile":
            best, best_s = caps[0], float("-inf")
            for m in caps:
                Lc = _copy_board(self.L)
                do_move(Lc, col, ligne, m[0], m[1], True)
                s = self.ai._evaluate(Lc, v)
                if s > best_s: best_s, best = s, m
            pick = best
        else:
            pick = random.choice(caps)
        tc, tl, _ = pick
        self.log_panel.append(f"🤖 rafle: {cell_name(col,ligne)} → {cell_name(tc,tl)}")
        chain = self._execute_move(col, ligne, tc, tl, True)
        if chain:
            self._ai_pending = time.time() + 0.45

    # ── undo ──

    def undo(self):
        if len(self.history_stack) <= 1: return
        if self._chain_piece:
            self._chain_piece = None; self._chain_count = 0
        self.history_stack.pop()
        L_cp, player, mv, score, last, hist = self.history_stack[-1]
        self.L = copy.deepcopy(L_cp)
        self.current_player = player
        self.move_number = mv
        self.score = copy.deepcopy(score)
        self._last_move = last
        self._game_over = False
        self.hover_piece = None; self.hover_moves = []
        self.hist_panel.set_lines(hist)
        self._turn_start = time.time()
        self.log_panel.append(f"← Annulation #{mv+1}")
        try: snd_undo()
        except: pass

    def new_game(self):
        self._init_state()
        self.hist_panel.clear()
        self.log_panel.clear()
        self.log_panel.append("=== Nouvelle partie ===")

    def save_game(self):
        data = {
            "board": self.L,
            "player": self.current_player,
            "move_number": self.move_number,
            "score": self.score,
            "last_move": self._last_move,
            "history_lines": self.hist_panel.lines,
            "theme_idx": self._theme_idx,
            "ai_mode_idx": self._ai_mode_idx,
            "c": self.c,
            "l": self.l,
            "N": N_PAWN_ROWS,
        }
        with open(self._save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.log_panel.append(f"Partie sauvegardée → {os.path.basename(self._save_path)}")

    def load_game(self):
        if not os.path.exists(self._save_path):
            self.log_panel.append("Aucune sauvegarde trouvée.")
            return
        with open(self._save_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.L = data["board"]
        self.current_player = data["player"]
        self.move_number = data["move_number"]
        self.score = {int(k): v for k, v in data["score"].items()}
        self._last_move = tuple(map(tuple, data.get("last_move", []))) if data.get("last_move") else None
        self.hist_panel.set_lines(data.get("history_lines", []))
        self._theme_idx = data.get("theme_idx", self._theme_idx) % len(THEME_NAMES)
        self._apply_theme()
        self._ai_mode_idx = data.get("ai_mode_idx", self._ai_mode_idx) % len(AI_LABELS)
        self._ai_mode = AI_MAP[self._ai_mode_idx]
        self.ai = SimpleAI(self._ai_mode, self.c, self.l) if self._ai_mode else None
        self._game_over = False
        self._chain_piece = None
        self._chain_count = 0
        self.hover_piece = None
        self.hover_moves = []
        self._turn_start = time.time()
        self._game_start = time.time()
        self.history_stack = []
        self._save_state()
        self.log_panel.append(f"Partie chargée ← {os.path.basename(self._save_path)}")

    def export_history(self):
        stamp = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self._export_dir, f"history_{stamp}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("Jeu de Dames — Historique des coups\n")
            f.write(f"Exporté le {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            for line in self.hist_panel.lines:
                f.write(line + "\n")
        self.log_panel.append(f"Historique exporté → {os.path.basename(path)}")

    def show_hint(self):
        if self._game_over or self._is_ai_turn(): return
        v = 1 if self.current_player == 1 else 0
        helper = SimpleAI("moyen", self.c, self.l)
        move = helper.choose_move(self.L, v)
        if not move: return
        fc, fl, tc, tl, _ = move
        self._hint = {(fc, fl), (tc, tl)}
        self._hint_expire = time.time() + 3
        self.log_panel.append(f"💡 Indice: {cell_name(fc,fl)} → {cell_name(tc,tl)}")

    # ── draw ──

    def draw(self):
        surf = self.screen
        surf.fill(BG)

        # Turn label
        if self._game_over:
            winner = "Les Blancs" if self.current_player == 1 else "Les Noirs"
            turn_txt = f"{winner} ont gagné!"
        else:
            turn_txt = "Tour des Noirs ●" if self.current_player == 1 else "Tour des Blancs ●"
        draw_text(surf, turn_txt, (self.board_x, 10), self.font_lg, GOLD if self._game_over else TEXT_CLR)

        # Timer
        elapsed = int(time.time() - self._turn_start)
        total = int(time.time() - self._game_start)
        m, s = divmod(elapsed, 60)
        tm, ts = divmod(total, 60)
        timer_txt = f"⏱ {m}:{s:02d}  (total {tm}:{ts:02d})"
        draw_text(surf, timer_txt, (self.board_x + COLS * SQ - 10, 14), self.font_md, DIM_CLR, "topright")

        # Score
        score_txt = f"Captures — Noir: {self.score[1]}  Blanc: {self.score[2]}"
        draw_text(surf, score_txt, (self.board_x, 38), self.font_md, DIM_CLR)

        # Column headers
        for col in range(COLS):
            cx = self.board_x + col * SQ + SQ // 2
            draw_text(surf, col_letter(col), (cx, self.board_y - 16), self.font_coord, DIM_CLR, "center")

        # Row labels
        for ligne in range(ROWS):
            cy = self.board_y + ligne * SQ + SQ // 2
            draw_text(surf, str(ligne + 1), (self.board_x - 16, cy), self.font_coord, DIM_CLR, "center")

        # Board squares + pieces
        hover_set = set()
        if self.hover_piece:
            hover_set.add(self.hover_piece)
        for m in self.hover_moves:
            hover_set.add((m[0], m[1]))

        now = time.time()
        for col in range(COLS):
            for ligne in range(ROWS):
                rect = self._cell_rect(col, ligne)
                bg = self._bg_for(col, ligne)

                if (col, ligne) in hover_set:
                    if (col, ligne) == self.hover_piece:
                        bg = HL_CHAIN if self._chain_piece else HL_PIECE
                    else:
                        bg = HL_MOVE

                # Flash animation for captured cells
                if (col, ligne) in self._flash_cells:
                    dt = now - self._flash_cells[(col, ligne)]
                    if dt < 0.4:
                        phase = int(dt / 0.1) % 2
                        bg = (255, 68, 68) if phase == 0 else bg
                    else:
                        del self._flash_cells[(col, ligne)]

                pygame.draw.rect(surf, bg, rect)

                # Piece
                p = self.L[col][ligne]
                if p[0] != 0:
                    cx, cy = rect.centerx, rect.centery
                    radius = SQ // 2 - 6
                    piece_clr = CLR_NOIR if p[0] == 1 else CLR_BLANC
                    draw_aa_circle(surf, piece_clr, (cx, cy), radius)
                    if p[1] == 2:
                        symbol = "♔" if p[0] == 1 else "♕"
                        crown_clr = (255, 215, 0) if p[0] == 1 else (80, 80, 80)
                        ts = self.font_piece.render(symbol, True, crown_clr)
                        surf.blit(ts, ts.get_rect(center=(cx, cy)))

        # Board border
        board_rect = pygame.Rect(self.board_x, self.board_y, COLS * SQ, ROWS * SQ)
        pygame.draw.rect(surf, (60, 60, 60), board_rect, 2)

        # Buttons
        mx, my = pygame.mouse.get_pos()
        for rect, label, _, col in self.buttons:
            draw_btn(surf, rect, label, self.font_md, col, rect.collidepoint(mx, my))

        # Theme / AI selector labels
        theme_label = f"Thème: {THEME_NAMES[self._theme_idx]} ▸"
        ai_label = f"Mode: {AI_LABELS[self._ai_mode_idx]} ▸"
        draw_text(surf, theme_label, (self._theme_rect.x, self._theme_rect.y + 4), self.font_md, DIM_CLR)
        draw_text(surf, ai_label, (self._ai_rect.x, self._ai_rect.y + 4), self.font_md, DIM_CLR)

        # Panels
        self.hist_panel.draw(surf)
        self.log_panel.draw(surf)

# ═══════════════════════════════════════════
# MENU
# ═══════════════════════════════════════════

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.font_title = pygame.font.SysFont("segoeui,arial", 48, bold=True)
        self.font_sub = pygame.font.SysFont("segoeui,arial", 16)
        self.font_btn = pygame.font.SysFont("segoeui,arial", 20, bold=True)
        self.font_label = pygame.font.SysFont("segoeui,arial", 16)

        self.ai_idx = 3
        self.theme_idx = 0

        cx = self.W // 2
        cy = self.H // 2

        self.ai_rect = pygame.Rect(cx + 10, cy - 60, 200, 32)
        self.theme_rect = pygame.Rect(cx + 10, cy - 18, 200, 32)
        self.start_btn = pygame.Rect(cx - 150, cy + 40, 300, 50)

    def set_screen(self, screen):
        self.screen = screen
        self.W, self.H = screen.get_size()
        cx = self.W // 2
        cy = self.H // 2
        self.ai_rect = pygame.Rect(cx + 10, cy - 60, 200, 32)
        self.theme_rect = pygame.Rect(cx + 10, cy - 18, 200, 32)
        self.start_btn = pygame.Rect(cx - 150, cy + 40, 300, 50)

    def draw(self):
        self.screen.fill(BG)
        cx = self.W // 2

        draw_text(self.screen, "♔  Jeu de Dames  ♕", (cx, self.H // 2 - 140),
                  self.font_title, GOLD, "center")
        draw_text(self.screen, "Checkers — Version Pygame", (cx, self.H // 2 - 90),
                  self.font_sub, DIM_CLR, "center")

        # AI mode selector
        draw_text(self.screen, "Mode de jeu:", (cx - 100, self.ai_rect.centery),
                  self.font_label, TEXT_CLR, "midright")
        pygame.draw.rect(self.screen, (42, 42, 42), self.ai_rect, border_radius=6)
        draw_text(self.screen, AI_LABELS[self.ai_idx], self.ai_rect.center,
                  self.font_label, TEXT_CLR, "center")

        # Theme selector
        draw_text(self.screen, "Thème:", (cx - 100, self.theme_rect.centery),
                  self.font_label, TEXT_CLR, "midright")
        pygame.draw.rect(self.screen, (42, 42, 42), self.theme_rect, border_radius=6)
        draw_text(self.screen, THEME_NAMES[self.theme_idx], self.theme_rect.center,
                  self.font_label, TEXT_CLR, "center")

        mx, my = pygame.mouse.get_pos()
        draw_btn(self.screen, self.start_btn, "▶  Commencer la partie", self.font_btn,
                 (45, 106, 79), self.start_btn.collidepoint(mx, my))

    def handle_click(self, pos):
        if self.ai_rect.collidepoint(pos):
            self.ai_idx = (self.ai_idx + 1) % len(AI_LABELS)
            return None
        if self.theme_rect.collidepoint(pos):
            self.theme_idx = (self.theme_idx + 1) % len(THEME_NAMES)
            return None
        if self.start_btn.collidepoint(pos):
            return ("start", AI_MAP[self.ai_idx], self.theme_idx)
        return None

# ═══════════════════════════════════════════
# MAIN LOOP (async for Pygbag)
# ═══════════════════════════════════════════

async def main():
    pygame.init()
    try:
        pygame.mixer.init(22050, -16, 1, 512)
        SOUND.enabled = True
    except Exception:
        SOUND.enabled = False

    # On desktop, start in fullscreen.
    # On web (emscripten), force windowed mode: FULLSCREEN at startup can stall.
    is_web = (sys.platform == "emscripten")
    if is_web:
        screen = pygame.display.set_mode((1280, 720))
    else:
        try:
            info = pygame.display.Info()
            screen = pygame.display.set_mode(
                (info.current_w, info.current_h), pygame.FULLSCREEN
            )
        except Exception:
            screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Jeu de Dames")
    clock = pygame.time.Clock()

    state = "menu"
    menu = Menu(screen)
    game = None
    is_fullscreen = True

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "menu":
                    result = menu.handle_click(event.pos)
                    if result and result[0] == "start":
                        _, ai_mode, theme_idx = result
                        game = DameGame(screen, ai_mode, theme_idx)
                        state = "game"
                elif state == "game":
                    result = game.handle_click(event.pos)
                    if result == "__MENU__":
                        state = "menu"
                        game = None
            elif event.type == pygame.MOUSEWHEEL:
                if state == "game" and game:
                    game.hist_panel.handle_scroll(event.y)
                    game.log_panel.handle_scroll(event.y)
            elif event.type == pygame.KEYDOWN and state == "game" and game:
                if event.mod & pygame.KMOD_CTRL:
                    if event.key == pygame.K_z: game.undo()
                    elif event.key == pygame.K_n: game.new_game()
                    elif event.key == pygame.K_h: game.show_hint()
                    elif event.key == pygame.K_s: game.save_game()
                    elif event.key == pygame.K_o: game.load_game()
                    elif event.key == pygame.K_e: game.export_history()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11 and not is_web:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    info = pygame.display.Info()
                    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((1280, 720))
                if menu:
                    menu.set_screen(screen)
                if game:
                    game.set_screen(screen)

        if state == "menu":
            menu.draw()
        elif state == "game" and game:
            mx, my = pygame.mouse.get_pos()
            game._update_hover(mx, my)
            game.update_ai()
            game.draw()

        pygame.display.flip()
        clock.tick(FPS)
        SOUND.update()
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
