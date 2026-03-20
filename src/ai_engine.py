# -*- coding: utf-8 -*-
"""
Classical draughts AI: iterative deepening, alpha-beta, quiescence (captures),
Zobrist transposition table, history + killer ordering, PST / mobility eval.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import ffdje
from ffdje import (
    Move,
    any_capture_available,
    apply_capture_no_promote,
    copy_board,
    get_all_moves,
    legal_chain_dests,
    sim_move_ai,
)

MATE_SCORE = 10000
TT_EXACT, TT_LOWER, TT_UPPER = 0, 1, 2


def _move_key(m: Move) -> int:
    fc, fl, tc, tl, cap = m
    return (fc << 24) | (fl << 16) | (tc << 8) | (tl << 4) | (1 if cap else 0)


def _build_pst(c: int, l: int) -> Tuple[list, list]:
    """Advancement bonus per cell for black (p_v=1) and white (p_v=0) pawns."""
    pb = [[0.0 for _ in range(l)] for _ in range(c)]
    pw = [[0.0 for _ in range(l)] for _ in range(c)]
    mid_r = (l - 1) / 2.0
    mid_c = (c - 1) / 2.0
    for col in range(c):
        for ligne in range(l):
            center = 0.08 * (1.0 - abs(ligne - mid_r) / max(mid_r, 1e-6))
            center += 0.05 * (1.0 - abs(col - mid_c) / max(mid_c, 1e-6))
            pb[col][ligne] = col * 0.15 + center
            pw[col][ligne] = (c - 1 - col) * 0.15 + center
    return pb, pw


@dataclass
class SearchConfig:
    max_depth: int
    time_ms: int
    use_tt: bool
    quiescence_max: int
    chain_search_depth: int  # plies after chain ends (ultra); 0 = eval only


PRESETS: Dict[str, SearchConfig] = {
    "facile": SearchConfig(0, 0, False, 0, 0),
    "moyen": SearchConfig(0, 0, False, 0, 0),
    "difficile": SearchConfig(2, 350, True, 0, 0),
    "ultra": SearchConfig(10, 1400, True, 10, 4),
}


class DraughtsAI:
    """AI for jeu de dames (same move encoding as GUI)."""

    def __init__(self, difficulty: str, c: int, l: int):
        self.difficulty = difficulty
        self.c = c
        self.l = l
        self.cfg = PRESETS.get(difficulty, PRESETS["difficile"])
        self._pst_b, self._pst_w = _build_pst(c, l)
        self._zobrist: Optional[List[List[List[int]]]] = None
        if self.cfg.use_tt:
            rnd = random.Random(0xD06F1A9)
            self._zobrist = [
                [
                    [rnd.getrandbits(64) for _ in range(5)]
                    for _ in range(l)
                ]
                for _ in range(c)
            ]
        self._tt: Dict[Tuple[int, int], Tuple[int, int, float, int]] = {}
        self._history: Dict[int, int] = {}
        self._killers: List[List[int]] = [[0, 0] for _ in range(96)]
        self._deadline = 0.0
        self._nodes = 0

    def _piece_zidx(self, p0, p1) -> int:
        if p0 == 0:
            return 0
        if p0 == 1:
            return 2 if p1 == 2 else 1
        return 4 if p1 == 2 else 3

    def _hash_board(self, L) -> int:
        h = 0
        for col in range(self.c):
            for ligne in range(self.l):
                p = L[col][ligne]
                idx = self._piece_zidx(p[0], p[1])
                h ^= self._zobrist[col][ligne][idx]
        return h

    def choose_move(self, L, v) -> Optional[Move]:
        moves = get_all_moves(L, v, self.c, self.l)
        if not moves:
            return None
        if self.difficulty == "facile":
            return random.choice(moves)
        if self.difficulty == "moyen":
            return self._greedy(L, v, moves)
        return self._iterative_deepening(L, v, moves)

    def choose_chain_capture(self, L, v, fc, fl) -> Optional[Tuple[int, int]]:
        dests = legal_chain_dests(L, v, fc, fl, self.c, self.l)
        if not dests:
            return None
        if self.difficulty == "facile":
            return random.choice(dests)
        if self.difficulty == "moyen":
            best_s, best_m = float("-inf"), dests[0]
            for tc, tl in dests:
                Lc = copy_board(L)
                apply_capture_no_promote(Lc, fc, fl, tc, tl)
                s = self._evaluate(Lc, v)
                if s > best_s:
                    best_s, best_m = s, (tc, tl)
            return best_m
        if self.difficulty == "ultra" and self.cfg.chain_search_depth > 0:
            best, best_m = float("-inf"), dests[0]
            for tc, tl in dests:
                Lc = copy_board(L)
                apply_capture_no_promote(Lc, fc, fl, tc, tl)
                val = self._chain_tree_value(Lc, tc, tl, v)
                if val > best:
                    best, best_m = val, (tc, tl)
            return best_m
        best_s, best_m = float("-inf"), dests[0]
        for tc, tl in dests:
            Lc = copy_board(L)
            apply_capture_no_promote(Lc, fc, fl, tc, tl)
            s = self._evaluate(Lc, v)
            if s > best_s:
                best_s, best_m = s, (tc, tl)
        return best_m

    def _chain_tree_value(self, L, fc, fl, v) -> float:
        ai_v = v
        subs = legal_chain_dests(L, v, fc, fl, self.c, self.l)
        if subs:
            best = float("-inf")
            for tc, tl in subs:
                Lc = copy_board(L)
                apply_capture_no_promote(Lc, fc, fl, tc, tl)
                val = self._chain_tree_value(Lc, tc, tl, v)
                best = max(best, val)
            return best
        self._nodes = 0
        self._deadline = time.perf_counter() + max(
            0.12, min(0.55, self.cfg.time_ms / 2200.0)
        )
        return self._search(
            L,
            self.cfg.chain_search_depth,
            False,
            ai_v,
            float("-inf"),
            float("inf"),
            0,
            use_tt=False,
        )

    def _greedy(self, L, v, moves: List[Move]) -> Move:
        scored = []
        for m in moves:
            Lc = copy_board(L)
            sim_move_ai(Lc, m, self.c)
            scored.append((self._evaluate(Lc, v), m))
        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][0]
        top = [s for s in scored if s[0] == best]
        return random.choice(top)[1]

    def _count_mobility(self, L, player_v) -> int:
        return len(get_all_moves(L, player_v, self.c, self.l))

    def _evaluate(self, L, ai_v) -> float:
        score = 0.0
        pieces = 0
        for col in range(self.c):
            for ligne in range(self.l):
                p = L[col][ligne]
                if p[0] == 0:
                    continue
                pieces += 1
                base = 5.0 if p[1] == 2 else 1.0
                p_v = 1 if p[0] == 1 else 0
                if p[1] == 1:
                    pst = self._pst_b[col][ligne] if p_v == 1 else self._pst_w[col][ligne]
                    base += pst * 0.25
                sign = 1.0 if p_v == ai_v else -1.0
                score += sign * base

        blend = min(1.0, pieces / 40.0)
        mob_w = 0.04 * (1.0 - 0.5 * blend)
        ma = self._count_mobility(L, ai_v)
        mo = self._count_mobility(L, 1 - ai_v)
        score += mob_w * (ma - mo)

        for col in range(self.c):
            for ligne in range(self.l):
                p = L[col][ligne]
                if p[0] == 0 or p[1] != 1:
                    continue
                p_v = 1 if p[0] == 1 else 0
                edge = 0.06 if (ligne == 0 or ligne == self.l - 1) else 0.0
                back = 0.05 if (p_v == 1 and col == 0) or (p_v == 0 and col == self.c - 1) else 0.0
                bonus = edge + back
                score += bonus if p_v == ai_v else -bonus
        return score

    def _iterative_deepening(self, L, v, moves: List[Move]) -> Move:
        self._deadline = time.perf_counter() + self.cfg.time_ms / 1000.0
        self._tt.clear()
        self._history.clear()
        best_move = moves[0]
        for depth in range(1, self.cfg.max_depth + 1):
            if time.perf_counter() >= self._deadline:
                break
            self._nodes = 0
            try:
                bm, bs = self._search_root(L, v, moves, depth)
            except _Timeout:
                break
            if bm is not None:
                best_move = bm
        return best_move

    def _search_root(self, L, v, moves: List[Move], depth: int) -> Tuple[Optional[Move], float]:
        tt_move = self._tt_probe_best(L, v)
        ordered = self._order_moves(moves, tt_move, None, 0)
        best_score = float("-inf")
        best_moves: List[Move] = []
        alpha, beta = float("-inf"), float("inf")
        for m in ordered:
            if time.perf_counter() >= self._deadline:
                raise _Timeout
            Lc = copy_board(L)
            sim_move_ai(Lc, m, self.c)
            sc = self._search(Lc, depth - 1, False, v, alpha, beta, 1, use_tt=True)
            if sc > best_score:
                best_score = sc
                best_moves = [m]
            elif sc == best_score:
                best_moves.append(m)
            alpha = max(alpha, best_score)
        return (random.choice(best_moves) if best_moves else None, best_score)

    def _tt_probe_best(self, L, stm) -> Optional[Move]:
        if not self.cfg.use_tt or not self._zobrist:
            return None
        key = (self._hash_board(L), stm)
        ent = self._tt.get(key)
        if not ent:
            return None
        _, _, _, mk = ent
        if mk == 0:
            return None
        return self._decode_move(mk)

    def _decode_move(self, mk: int) -> Move:
        cap = (mk & 1) == 1
        tl = (mk >> 4) & 0xFF
        tc = (mk >> 8) & 0xFF
        fl = (mk >> 16) & 0xFF
        fc = (mk >> 24) & 0xFF
        return (fc, fl, tc, tl, cap)

    def _tt_probe(
        self, L, stm, depth, alpha, beta
    ) -> Optional[float]:
        if not self.cfg.use_tt or not self._zobrist:
            return None
        key = (self._hash_board(L), stm)
        ent = self._tt.get(key)
        if not ent:
            return None
        d_stored, flag, sc, _ = ent
        if d_stored < depth:
            return None
        if flag == TT_EXACT:
            return sc
        if flag == TT_LOWER:
            if sc >= beta:
                return sc
            return None
        if flag == TT_UPPER:
            if sc <= alpha:
                return sc
            return None
        return None

    def _tt_store(self, L, stm, depth, flag, score, best_move: Optional[Move]):
        if not self.cfg.use_tt or not self._zobrist:
            return
        key = (self._hash_board(L), stm)
        mk = _move_key(best_move) if best_move else 0
        prev = self._tt.get(key)
        if prev and prev[0] > depth:
            return
        self._tt[key] = (depth, flag, float(score), mk)

    def _order_moves(
        self,
        moves: List[Move],
        tt_move: Optional[Move],
        parent_move: Optional[Move],
        ply: int,
    ) -> List[Move]:
        kp = min(ply, len(self._killers) - 1)

        def score(m):
            pri = 0
            if tt_move and m == tt_move:
                pri += 1_000_000
            if m[4]:
                pri += 50_000
            k1, k2 = self._killers[kp]
            mk = _move_key(m)
            if mk == k1:
                pri += 30_000
            elif mk == k2:
                pri += 29_000
            pri += self._history.get(mk, 0)
            return -pri

        return sorted(moves, key=score)

    def _search(
        self,
        L,
        depth: int,
        maximizing: bool,
        ai_v: int,
        alpha: float,
        beta: float,
        ply: int,
        use_tt: bool = True,
    ) -> float:
        self._nodes += 1
        if self._nodes % 2000 == 0 and time.perf_counter() >= self._deadline:
            raise _Timeout
        stm = ai_v if maximizing else (1 - ai_v)
        if use_tt:
            tsc = self._tt_probe(L, stm, depth, alpha, beta)
            if tsc is not None:
                return float(tsc)

        moves = get_all_moves(L, stm, self.c, self.l)
        if not moves:
            val = -MATE_SCORE if maximizing else MATE_SCORE
            if use_tt:
                self._tt_store(L, stm, depth, TT_EXACT, val, None)
            return val

        if depth == 0:
            if self.cfg.quiescence_max > 0 and any_capture_available(L, stm, self.c, self.l):
                val = self._quiescence(
                    L,
                    self.cfg.quiescence_max,
                    maximizing,
                    ai_v,
                    alpha,
                    beta,
                    ply,
                    use_tt=False,
                )
            else:
                val = self._evaluate(L, ai_v)
            if use_tt:
                self._tt_store(L, stm, depth, TT_EXACT, val, None)
            return val

        tt_best = self._tt_probe_best(L, stm) if use_tt else None
        ordered = self._order_moves(moves, tt_best, None, ply)
        best_move: Optional[Move] = None
        original_alpha = alpha

        if maximizing:
            val = float("-inf")
            for m in ordered:
                Lc = copy_board(L)
                sim_move_ai(Lc, m, self.c)
                sc = self._search(
                    Lc, depth - 1, False, ai_v, alpha, beta, ply + 1, use_tt=use_tt
                )
                if sc > val:
                    val = sc
                    best_move = m
                alpha = max(alpha, val)
                if beta <= alpha:
                    self._update_heuristics(m, ply)
                    break
        else:
            val = float("inf")
            for m in ordered:
                Lc = copy_board(L)
                sim_move_ai(Lc, m, self.c)
                sc = self._search(
                    Lc, depth - 1, True, ai_v, alpha, beta, ply + 1, use_tt=use_tt
                )
                if sc < val:
                    val = sc
                    best_move = m
                beta = min(beta, val)
                if beta <= alpha:
                    self._update_heuristics(m, ply)
                    break

        if maximizing:
            if val <= original_alpha:
                flag = TT_UPPER
            elif val >= beta:
                flag = TT_LOWER
            else:
                flag = TT_EXACT
        else:
            if val >= beta:
                flag = TT_LOWER
            elif val <= original_alpha:
                flag = TT_UPPER
            else:
                flag = TT_EXACT
        if use_tt:
            self._tt_store(L, stm, depth, flag, val, best_move)
        return val

    def _update_heuristics(self, m: Move, ply: int):
        mk = _move_key(m)
        if not m[4]:
            kp = min(ply, len(self._killers) - 1)
            k1 = self._killers[kp][0]
            if mk != k1:
                self._killers[kp][1] = k1
                self._killers[kp][0] = mk
        self._history[mk] = self._history.get(mk, 0) + depth_bonus(ply)

    def _quiescence(
        self,
        L,
        qdepth: int,
        maximizing: bool,
        ai_v: int,
        alpha: float,
        beta: float,
        ply: int,
        use_tt: bool = False,
    ) -> float:
        stand = self._evaluate(L, ai_v)
        if maximizing:
            if stand >= beta:
                return stand
            alpha = max(alpha, stand)
        else:
            if stand <= alpha:
                return stand
            beta = min(beta, stand)

        stm = ai_v if maximizing else (1 - ai_v)
        caps = [m for m in get_all_moves(L, stm, self.c, self.l) if m[4]]
        if not caps or qdepth <= 0:
            return stand

        tt_best = self._tt_probe_best(L, stm) if use_tt else None
        ordered = self._order_moves(caps, tt_best, None, ply)
        val = stand
        if maximizing:
            for m in ordered:
                Lc = copy_board(L)
                sim_move_ai(Lc, m, self.c)
                sc = self._quiescence(
                    Lc, qdepth - 1, False, ai_v, alpha, beta, ply + 1, use_tt=use_tt
                )
                val = max(val, sc)
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
        else:
            for m in ordered:
                Lc = copy_board(L)
                sim_move_ai(Lc, m, self.c)
                sc = self._quiescence(
                    Lc, qdepth - 1, True, ai_v, alpha, beta, ply + 1, use_tt=use_tt
                )
                val = min(val, sc)
                beta = min(beta, val)
                if beta <= alpha:
                    break
        return val


class _Timeout(Exception):
    pass


def depth_bonus(ply: int) -> int:
    return ply * ply + 1


# Backward-compatible alias
SimpleAI = DraughtsAI
