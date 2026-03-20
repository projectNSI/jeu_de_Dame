# -*- coding: utf-8 -*-
"""
FFDJE-style draughts rules (10×10, max capture, deferred promotion during rafle).
Shared by GUI and AI.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from damedemain import is_friendly, jeu_possible

DIAGS = [[-1, 1], [1, 1], [-1, -1], [1, -1]]

Move = Tuple[int, int, int, int, bool]


def copy_board(L):
    return [[[cell[0], cell[1], cell[2]] for cell in col] for col in L]


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


def _enemy_sq(L, fc, fl, tc, tl):
    dc = 1 if tc > fc else -1
    dl = 1 if tl > fl else -1
    sc, sl = fc + dc, fl + dl
    while (sc, sl) != (tc, tl):
        if L[sc][sl][0] != 0:
            return sc, sl, L[sc][sl][1] == 2
        sc += dc
        sl += dl
    return None, None, False


def apply_capture_no_promote(L, fc, fl, tc, tl):
    """Capture; piece keeps type (pion stays pion on dame row during rafle).
    Returns (col, ligne) of the captured square, or None."""
    sc, sl, _ = _enemy_sq(L, fc, fl, tc, tl)
    if sc is None:
        return None
    do_move(L, fc, fl, tc, tl, True)
    return (sc, sl)


def apply_quiet_move(L, fc, fl, tc, tl, c_max):
    """Simple move + immediate promotion if applicable (fin de coup)."""
    do_move(L, fc, fl, tc, tl, False)
    tc, tl = tc, tl
    if L[tc][tl][1] == 1:
        color = L[tc][tl][0]
        if (color == 1 and tc == c_max - 1) or (color == 2 and tc == 0):
            L[tc][tl][1] = 2


def maybe_promote_end_of_turn(L, tc, tl, c_max):
    """After full rafle or turn, crown man on last rank."""
    if L[tc][tl][1] == 1:
        color = L[tc][tl][0]
        if (color == 1 and tc == c_max - 1) or (color == 2 and tc == 0):
            L[tc][tl][1] = 2


def _has_captures(L, col, ligne, v):
    J = jeu_possible(L, col, ligne, DIAGS, v, None)
    if not J:
        return False
    if isinstance(J[0], list):
        return any(
            J[tc][tl] == 1 for tc in range(len(J)) for tl in range(len(J[0]))
        )
    return any(j == 1 for j in J)


def any_capture_available(L, v, c_max, l_max) -> bool:
    for col in range(c_max):
        for ligne in range(l_max):
            if is_friendly(L, col, ligne, v) and _has_captures(L, col, ligne, v):
                return True
    return False


def raw_captures_from_piece(L, fc, fl, v, c_max, l_max) -> List[Tuple[int, int]]:
    if not is_friendly(L, fc, fl, v):
        return []
    must = any_capture_available(L, v, c_max, l_max)
    if must and not _has_captures(L, fc, fl, v):
        return []
    J = jeu_possible(L, fc, fl, DIAGS, v, None)
    mv = get_moves(L, fc, fl, J, v)
    if must:
        mv = [m for m in mv if m[2]]
    return [(m[0], m[1]) for m in mv if m[2]]


def raw_captures_piece_only(L, fc, fl, v, c_max, l_max) -> List[Tuple[int, int]]:
    """All capture landings from (fc,fl) — used mid-rafle (no global must filter)."""
    if not is_friendly(L, fc, fl, v):
        return []
    J = jeu_possible(L, fc, fl, DIAGS, v, None)
    if not J:
        return []
    mv = get_moves(L, fc, fl, J, v)
    return [(m[0], m[1]) for m in mv if m[2]]


def _cmp_score(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
    return a > b


def best_chain_score(L, v, fc, fl, c_max, l_max) -> Tuple[int, int]:
    """Max (pieces, dames_prises) from a continuing rafle at (fc,fl)."""
    caps = raw_captures_piece_only(L, fc, fl, v, c_max, l_max)
    if not caps:
        return (0, 0)
    best = (-1, -1)
    for tc, tl in caps:
        es, _, was_king = _enemy_sq(L, fc, fl, tc, tl)
        if es is None:
            continue
        Lc = copy_board(L)
        apply_capture_no_promote(Lc, fc, fl, tc, tl)
        sub = best_chain_score(Lc, v, tc, tl, c_max, l_max)
        tot = 1 + sub[0]
        dk = (1 if was_king else 0) + sub[1]
        cand = (tot, dk)
        if _cmp_score(cand, best):
            best = cand
    return best


def global_max_capture_score(L, v, c_max, l_max) -> Tuple[int, int]:
    """Best (total captures, kings captured) for side v this turn."""
    if not any_capture_available(L, v, c_max, l_max):
        return (0, 0)
    best = (-1, -1)
    for fc in range(c_max):
        for fl in range(l_max):
            if not is_friendly(L, fc, fl, v):
                continue
            for tc, tl in raw_captures_from_piece(L, fc, fl, v, c_max, l_max):
                es, _, was_king = _enemy_sq(L, fc, fl, tc, tl)
                if es is None:
                    continue
                Lc = copy_board(L)
                apply_capture_no_promote(Lc, fc, fl, tc, tl)
                sub = best_chain_score(Lc, v, tc, tl, c_max, l_max)
                tot = 1 + sub[0]
                dk = (1 if was_king else 0) + sub[1]
                cand = (tot, dk)
                if _cmp_score(cand, best):
                    best = cand
    return best if best[0] >= 0 else (0, 0)


def legal_first_moves(L, v, c_max, l_max) -> List[Move]:
    """All legal moves at start of turn (max capture + quiet if no capture)."""
    moves: List[Move] = []
    if any_capture_available(L, v, c_max, l_max):
        target = global_max_capture_score(L, v, c_max, l_max)
        for fc in range(c_max):
            for fl in range(l_max):
                if not is_friendly(L, fc, fl, v):
                    continue
                for tc, tl in raw_captures_from_piece(L, fc, fl, v, c_max, l_max):
                    es, _, was_king = _enemy_sq(L, fc, fl, tc, tl)
                    if es is None:
                        continue
                    Lc = copy_board(L)
                    apply_capture_no_promote(Lc, fc, fl, tc, tl)
                    sub = best_chain_score(Lc, v, tc, tl, c_max, l_max)
                    sc = (1 + sub[0], (1 if was_king else 0) + sub[1])
                    if sc == target:
                        moves.append((fc, fl, tc, tl, True))
        return moves
    for fc in range(c_max):
        for fl in range(l_max):
            if not is_friendly(L, fc, fl, v):
                continue
            J = jeu_possible(L, fc, fl, DIAGS, v, None)
            for m in get_moves(L, fc, fl, J, v):
                if not m[2]:
                    moves.append((fc, fl, m[0], m[1], False))
    return moves


def legal_chain_dests(L, v, fc, fl, c_max, l_max) -> List[Tuple[int, int]]:
    """Landing squares for max-compliant continuations from (fc,fl) during rafle."""
    caps = raw_captures_piece_only(L, fc, fl, v, c_max, l_max)
    if not caps:
        return []
    target = best_chain_score(L, v, fc, fl, c_max, l_max)
    out: List[Tuple[int, int]] = []
    for tc, tl in caps:
        es, _, was_king = _enemy_sq(L, fc, fl, tc, tl)
        if es is None:
            continue
        Lc = copy_board(L)
        apply_capture_no_promote(Lc, fc, fl, tc, tl)
        sub = best_chain_score(Lc, v, tc, tl, c_max, l_max)
        sc = (1 + sub[0], (1 if was_king else 0) + sub[1])
        if sc == target:
            out.append((tc, tl))
    return out


def legal_moves_to_hover(
    L, v, fc, fl, c_max, l_max, chain_piece: Optional[Tuple[int, int]]
) -> List[Tuple[int, int, bool, bool]]:
    """
    Returns list of (tc, tl, is_capture, is_mandatory_capture_context) for UI.
    is_mandatory_capture_context True when global capture applies (fluo highlight).
    """
    must = any_capture_available(L, v, c_max, l_max)
    if chain_piece:
        cc, cl = chain_piece
        if (cc, cl) != (fc, fl):
            return []
        dests = legal_chain_dests(L, v, fc, fl, c_max, l_max)
        return [(tc, tl, True, must) for tc, tl in dests]
    out: List[Tuple[int, int, bool, bool]] = []
    for m in legal_first_moves(L, v, c_max, l_max):
        fc2, fl2, tc, tl, cap = m
        if fc2 == fc and fl2 == fl:
            out.append((tc, tl, cap, must and cap))
    return out


def is_move_legal(L, v, fc, fl, tc, tl, is_cap, c_max, l_max, chain_piece) -> bool:
    if chain_piece:
        if chain_piece != (fc, fl) or not is_cap:
            return False
        return (tc, tl) in legal_chain_dests(L, v, fc, fl, c_max, l_max)
    for m in legal_first_moves(L, v, c_max, l_max):
        if m == (fc, fl, tc, tl, is_cap):
            return True
    return False


def get_all_moves(L, v, c_max, l_max) -> List[Move]:
    """Root legal moves (for AI / win detection)."""
    return legal_first_moves(L, v, c_max, l_max)


def sim_move_ai(L, move: Move, c_max):
    """One step for search: capture without mid-promote; quiet with promote."""
    fc, fl, tc, tl, is_cap = move
    if is_cap:
        apply_capture_no_promote(L, fc, fl, tc, tl)
    else:
        apply_quiet_move(L, fc, fl, tc, tl, c_max)
