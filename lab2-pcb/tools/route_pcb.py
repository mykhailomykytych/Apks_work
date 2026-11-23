"""Simple two-layer grid router (A*) for the lab 2 board.

* grid 0.25 mm, layers F.Cu / B.Cu, vias between layers;
* 8 directions (0/45/90 deg), turns sharper than 90 deg are forbidden,
  every turn and every via has a cost -> short tracks without acute angles;
* clearances are enforced geometrically with a safety margin, the final
  board is verified by KiCad DRC (tools/build_pcb.py drc);
* multi-pin nets are routed as a tree: each next pin is connected to the
  nearest point of the already routed part of the net;
* if some net cannot be routed, the order of nets is changed (rip-up & retry).

Run with the KiCad python:  /usr/bin/python3 tools/route_pcb.py
"""
import heapq
import itertools
import math
import os
import random
import sys

import numpy as np
import pcbnew

sys.path.insert(0, os.path.dirname(__file__))
import build_pcb as B  # noqa: E402

G = 0.25                       # grid step, mm
TW = B.TRACK_W                 # track width
CLR = B.CLEARANCE              # clearance
MARGIN = 0.06                  # safety margin for grid discretisation
VIA_R = B.VIA_D / 2
EDGE_CLR = 0.6
VIA_COST = 6.0
TURN_COST = 0.6
PREF_COST = 0.15               # small penalty: F.Cu prefers horizontal, B.Cu vertical

NX = int(round(B.W / G)) + 1
NY = int(round(B.H / G)) + 1
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


def cell_xy(i, j):
    return i * G, j * G


class Grid:
    def __init__(self):
        # owner[layer, i, j]: -1 free, >=0 net id that blocks it, -2 several / board edge
        self.own_t = np.full((2, NX, NY), -1, dtype=np.int32)   # for track centres
        self.own_v = np.full((NX, NY), -1, dtype=np.int32)      # for via centres (both layers)
        xs = np.arange(NX)[:, None] * G
        ys = np.arange(NY)[None, :] * G
        self.xs, self.ys = xs, ys
        # board edge (rounded rectangle, inset)
        for arr, inset in ((self.own_t[0], EDGE_CLR + TW / 2), (self.own_t[1], EDGE_CLR + TW / 2), (self.own_v, EDGE_CLR + VIA_R)):
            cx = np.clip(xs, B.R, B.W - B.R)
            cy = np.clip(ys, B.R, B.H - B.R)
            d_out = B.R - np.hypot(xs - cx, ys - cy)       # distance to the rounded outline
            arr[d_out < inset] = -2

    def _mark(self, arr, net, mask):
        cur = arr[mask]
        cur = np.where(cur == -1, net, np.where(cur == net, net, -2))
        arr[mask] = cur

    def add_disc(self, net, x, y, r, layers=(0, 1)):
        """Copper disc of radius r (pad or via) owned by `net`."""
        d = np.hypot(self.xs - x, self.ys - y)
        for L in layers:
            self._mark(self.own_t[L], net, d < r + CLR + TW / 2 + MARGIN)
        self._mark(self.own_v, net, d < r + CLR + VIA_R + MARGIN)

    def add_segment(self, net, a, b, layer):
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        ll = dx * dx + dy * dy or 1e-9
        t = np.clip(((self.xs - ax) * dx + (self.ys - ay) * dy) / ll, 0, 1)
        d = np.hypot(self.xs - (ax + t * dx), self.ys - (ay + t * dy))
        self._mark(self.own_t[layer], net, d < TW + CLR + MARGIN)
        self._mark(self.own_v, net, d < TW / 2 + CLR + VIA_R + MARGIN)

    def free_t(self, net, L, i, j):
        o = self.own_t[L, i, j]
        return o == -1 or o == net

    def free_v(self, net, i, j):
        o = self.own_v[i, j]
        return o == -1 or o == net


def astar(grid, net, sources, targets):
    """sources/targets: sets of (L, i, j). Returns list of (L, i, j)."""
    tl = list(targets)
    tx = np.array([t[1] for t in tl])
    ty = np.array([t[2] for t in tl])

    def h(i, j):
        return float(np.min(np.hypot(tx - i, ty - j))) * G

    openq, best, parent, pdir = [], {}, {}, {}
    cnt = itertools.count()
    for s in sources:
        best[s] = 0.0
        pdir[s] = None
        heapq.heappush(openq, (h(s[1], s[2]), next(cnt), s))
    while openq:
        _, _, cur = heapq.heappop(openq)
        if cur in targets:
            path = [cur]
            while cur in parent:
                cur = parent[cur]
                path.append(cur)
            return path[::-1]
        L, i, j = cur
        g0 = best[cur]
        d0 = pdir[cur]
        # planar moves
        for k, (di, dj) in enumerate(DIRS):
            if d0 is not None and d0 != "via":
                diff = min((k - d0) % 8, (d0 - k) % 8)
                if diff > 2:                       # sharper than 90 deg
                    continue
                turn = TURN_COST * diff
            else:
                turn = 0.0
            ni, nj = i + di, j + dj
            if not (0 <= ni < NX and 0 <= nj < NY) or not grid.free_t(net, L, ni, nj):
                continue
            step = G * (math.sqrt(2) if di and dj else 1.0)
            pref = PREF_COST * step if (L == 0 and dj and not di) or (L == 1 and di and not dj) else 0.0
            ng = g0 + step + turn + pref
            nxt = (L, ni, nj)
            if ng < best.get(nxt, 1e18):
                best[nxt], parent[nxt], pdir[nxt] = ng, cur, k
                heapq.heappush(openq, (ng + h(ni, nj), next(cnt), nxt))
        # via
        if grid.free_v(net, i, j) and grid.free_t(net, 1 - L, i, j):
            nxt = (1 - L, i, j)
            ng = g0 + VIA_COST
            if ng < best.get(nxt, 1e18):
                best[nxt], parent[nxt], pdir[nxt] = ng, cur, "via"
                heapq.heappush(openq, (ng + h(i, j), next(cnt), nxt))
    return None


def pad_geometry(board):
    """net name -> list of (x, y, r) in board-relative mm."""
    pads = {}
    for fp in board.GetFootprints():
        for p in fp.Pads():
            pos = p.GetPosition()
            x = pcbnew.ToMM(pos.x) - B.X0
            y = pcbnew.ToMM(pos.y) - B.Y0
            r = pcbnew.ToMM(p.GetSize().x) / 2                      # inscribed radius
            if p.GetShape() == pcbnew.PAD_SHAPE_RECT:
                ro = r * math.sqrt(2)                                  # rect corners
            else:
                ro = r
            pads.setdefault(p.GetNetname(), []).append((x, y, r, ro))
    return pads


def pad_cells(x, y, r):
    cells = set()
    rr = r - TW / 2 - 0.05          # track end stays completely inside the pad
    for i in range(int((x - r) / G) - 1, int((x + r) / G) + 2):
        for j in range(int((y - r) / G) - 1, int((y + r) / G) + 2):
            if 0 <= i < NX and 0 <= j < NY and math.hypot(i * G - x, j * G - y) <= rr:
                for L in (0, 1):
                    cells.add((L, i, j))
    return cells


def simplify(path):
    """Grid path -> list of ('seg', L, a, b) and ('via', x, y)."""
    items, start = [], 0
    for k in range(1, len(path) + 1):
        end_run = k == len(path) or path[k][0] != path[start][0] or (
            k - start >= 2 and (path[k][1] - path[k - 1][1], path[k][2] - path[k - 1][2])
            != (path[k - 1][1] - path[k - 2][1], path[k - 1][2] - path[k - 2][2])
        )
        if end_run:
            if k - 1 > start:
                L = path[start][0]
                items.append(("seg", L, cell_xy(*path[start][1:]), cell_xy(*path[k - 1][1:])))
            if k < len(path) and path[k][0] != path[k - 1][0]:
                items.append(("via", *cell_xy(*path[k][1:])))
                start = k
            else:
                start = k - 1
    return items


def route_all(board, order):
    pads = pad_geometry(board)
    names = list(pads)
    nid = {n: k for k, n in enumerate(names)}
    grid = Grid()
    for n, plist in pads.items():
        for x, y, _, ro in plist:
            grid.add_disc(nid[n], x, y, ro)
    result, failed = {}, []
    for n in order:
        k = nid[n]
        plist = pads[n]
        tree_cells = pad_cells(*plist[0][:3])
        anchors = {c: plist[0] for c in tree_cells}
        remaining = list(plist[1:])
        items = []
        ok = True
        while remaining:
            # nearest remaining pad to the current tree
            remaining.sort(key=lambda p: min(math.hypot(c[1] * G - p[0], c[2] * G - p[1]) for c in tree_cells))
            p = remaining.pop(0)
            tgt = pad_cells(*p[:3])
            path = astar(grid, k, tree_cells, tgt)
            if path is None:
                ok = False
                break
            segs = simplify(path)
            # connect the path ends to the pad centres
            s_anchor = anchors.get(path[0])
            if s_anchor:
                segs.insert(0, ("seg", path[0][0], (s_anchor[0], s_anchor[1]), cell_xy(*path[0][1:])))
            segs.append(("seg", path[-1][0], cell_xy(*path[-1][1:]), (p[0], p[1])))
            for it in segs:
                if it[0] == "seg":
                    if it[2] != it[3]:
                        grid.add_segment(k, it[2], it[3], it[1])
                else:
                    grid.add_disc(k, it[1], it[2], VIA_R)
            items += [it for it in segs if it[0] == "via" or it[2] != it[3]]
            new_cells = set(path) | tgt
            tree_cells |= new_cells
            for c in tgt:
                anchors[c] = p
        if ok:
            result[n] = items
        else:
            failed.append(n)
    return result, failed


def write_board(board, routes):
    for t in list(board.GetTracks()):
        board.Remove(t)
    for n, items in routes.items():
        ni = board.FindNet(n)
        for it in items:
            if it[0] == "seg":
                tr = pcbnew.PCB_TRACK(board)
                tr.SetStart(B.pt(*it[2]))
                tr.SetEnd(B.pt(*it[3]))
                tr.SetWidth(B.mm(TW))
                tr.SetLayer(pcbnew.F_Cu if it[1] == 0 else pcbnew.B_Cu)
                tr.SetNet(ni)
                board.Add(tr)
            else:
                v = pcbnew.PCB_VIA(board)
                v.SetPosition(B.pt(it[1], it[2]))
                v.SetWidth(B.mm(B.VIA_D))
                v.SetDrill(B.mm(B.VIA_DRILL))
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                v.SetNet(ni)
                board.Add(v)


def stats(routes):
    length = sum(math.dist(it[2], it[3]) for items in routes.values() for it in items if it[0] == "seg")
    vias = sum(1 for items in routes.values() for it in items if it[0] == "via")
    return length, vias


def main():
    board = pcbnew.LoadBoard(B.PCB)
    pads = pad_geometry(board)
    nets = [n for n in pads if n and len(pads[n]) > 1]

    def span(n):
        p = pads[n]
        return sum(math.dist(a[:2], b[:2]) for a, b in zip(p, p[1:]))

    base = sorted(nets, key=span)
    best = None
    rnd = random.Random(407)
    orders = [base, base[::-1]] + [rnd.sample(base, len(base)) for _ in range(30)]
    for attempt, order in enumerate(orders, 1):
        routes, failed = route_all(board, order)
        length, vias = stats(routes)
        print(f"attempt {attempt:2}: failed={failed} length={length:.1f} mm vias={vias}")
        if not failed and (best is None or (length + 3 * vias) < (best[1] + 3 * best[2])):
            best = (routes, length, vias)
        if best and attempt >= 6:
            break
    if best is None:
        raise SystemExit("routing failed for every net order")
    write_board(board, best[0])
    pcbnew.SaveBoard(B.PCB, board)
    print(f"routed: total track length {best[1]:.1f} mm, vias {best[2]}")


if __name__ == "__main__":
    main()
