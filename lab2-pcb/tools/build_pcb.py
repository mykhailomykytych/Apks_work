"""Build, route and verify the PCB with the KiCad 7 Python API.

Steps
  place   : board outline (credit card 85.6 x 53.98 mm, R3.18 corners),
            footprints, nets  -> kicad/lab2_guid_pcb.kicad_pcb (unrouted)
            and Specctra DSN   -> build/lab2_guid_pcb.dsn
  import  : read Freerouting result build/lab2_guid_pcb.ses, add tracks/vias
  drc     : write DRC report  -> out/drc_report.txt

Must be run with the system python that has the `pcbnew` module:
  /usr/bin/python3 tools/build_pcb.py place|import|drc
"""
import math
import os
import re
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(__file__))
from guid_design import GUID, all_nets, components  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KICAD = os.path.join(ROOT, "kicad")
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "out")
PCB = os.path.join(KICAD, "lab2_guid_pcb.kicad_pcb")
DSN = os.path.join(BUILD, "lab2_guid_pcb.dsn")
SES = os.path.join(BUILD, "lab2_guid_pcb.ses")
FPLIB = os.path.join(KICAD, "guid_parts.pretty")

# Board: credit card ID-1 format
X0, Y0 = 100.0, 100.0
W, H, R = 85.6, 53.98, 3.18

# Placement (board-relative mm): most connected parts are closest to each other.
# U5 (hub, 12 pins) in the middle, U1 (8 pins, shares 4 nets with U5) to its left,
# J1 on the short (left) edge next to U1, which owns 3 of the 4 free pins.
PLACEMENT = {
    "J1": (5.0, 27.0, 0),
    "U1": (22.0, 22.0, 0),
    "U2": (20.0, 40.0, 0),
    "U4": (34.0, 39.0, 0),
    "U5": (46.0, 22.0, 0),
    "U3": (64.0, 18.0, 0),
}

TRACK_W = 0.3     # mm
CLEARANCE = 0.25  # mm
VIA_D, VIA_DRILL = 0.8, 0.4


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(X0 + x), mm(Y0 + y))


def add_outline(board):
    """Rounded rectangle on Edge.Cuts."""
    def seg(a, b):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pt(*a))
        s.SetEnd(pt(*b))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        board.Add(s)

    def arc(c, start, end, mid_deg):
        """Corner arc; mid_deg = direction from the centre to the arc middle."""
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        a = math.radians(mid_deg)
        m = (c[0] + R * math.cos(a), c[1] + R * math.sin(a))
        s.SetArcGeometry(pt(*start), pt(*m), pt(*end))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        board.Add(s)

    seg((R, 0), (W - R, 0))
    seg((W, R), (W, H - R))
    seg((W - R, H), (R, H))
    seg((0, H - R), (0, R))
    arc((W - R, R), (W - R, 0), (W, R), -45)        # top right
    arc((W - R, H - R), (W, H - R), (W - R, H), 45)  # bottom right
    arc((R, H - R), (R, H), (0, H - R), 135)         # bottom left
    arc((R, R), (0, R), (R, 0), 225)                 # top left


def add_text(board, text, x, y, size=1.0, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(pt(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15))
    board.Add(t)


def place():
    os.makedirs(BUILD, exist_ok=True)
    board = pcbnew.NewBoard(PCB)
    board.SetCopperLayerCount(2)

    ds = board.GetDesignSettings()
    ds.m_MinClearance = mm(0.2)
    ds.m_TrackMinWidth = mm(0.2)
    ds.m_CopperEdgeClearance = mm(0.5)
    nc = ds.m_NetSettings.m_DefaultNetClass
    nc.SetClearance(mm(CLEARANCE))
    nc.SetTrackWidth(mm(TRACK_W))
    nc.SetViaDiameter(mm(VIA_D))
    nc.SetViaDrill(mm(VIA_DRILL))

    add_outline(board)

    # nets
    netinfo = {}
    for name in all_nets():
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni
    pad_net = {}
    for name, pins in all_nets().items():
        for ref, p in pins:
            pad_net[(ref, str(p))] = netinfo[name]

    sizes = {ref: side for ref, _, side in components()}
    for ref, (x, y, rot) in PLACEMENT.items():
        fp_name = f"GUID_{ref}_{sizes[ref]}x{sizes[ref]}mm" if ref != "J1" else "GUID_J1_1x04_P2.54mm"
        fp = pcbnew.FootprintLoad(FPLIB, fp_name)
        fp.SetFPID(pcbnew.LIB_ID("guid_parts", fp_name))
        fp.SetReference(ref)
        fp.SetValue(fp_name)
        fp.SetPosition(pt(x, y))
        fp.SetOrientationDegrees(rot)
        board.Add(fp)
        for pad in fp.Pads():
            n = pad_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(n)

    add_text(board, "LAB2 KI-407 Mykytych M.V.", 62.0, 47.0, 1.0)
    add_text(board, GUID, 62.0, 50.0, 0.8)

    pcbnew.SaveBoard(PCB, board)
    if not pcbnew.ExportSpecctraDSN(board, DSN):
        raise SystemExit("DSN export failed")
    print("placed board saved:", PCB)
    print("DSN exported:", DSN)


def parse_ses(path):
    text = open(path).read()
    m = re.search(r"\(resolution\s+(\w+)\s+(\d+)\)", text)
    unit, res = m.group(1), int(m.group(2))
    scale = {"um": 0.001, "mm": 1.0, "mil": 0.0254, "inch": 25.4}[unit] / res
    wires, vias = [], []
    # split by net blocks
    for nm in re.finditer(r"\(net\s+(\"[^\"]*\"|\S+)(.*?)(?=\(net\s|\Z)", text, re.S):
        net = nm.group(1).strip('"')
        body = nm.group(2)
        for w in re.finditer(r"\(path\s+(\S+)\s+(\d+)\s+([-\d\s]+)\)", body):
            layer, width = w.group(1), int(w.group(2)) * scale
            nums = [int(v) for v in w.group(3).split()]
            pts = [(nums[i] * scale, -nums[i + 1] * scale) for i in range(0, len(nums), 2)]
            wires.append((net, layer, width, pts))
        for v in re.finditer(r"\(via\s+(\"[^\"]*\"|\S+)\s+(-?\d+)\s+(-?\d+)", body):
            vias.append((net, int(v.group(2)) * scale, -int(v.group(3)) * scale))
    return wires, vias


def import_ses():
    board = pcbnew.LoadBoard(PCB)
    for t in list(board.GetTracks()):
        board.Remove(t)
    wires, vias = parse_ses(SES)
    layers = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    for net, layer, width, pts in wires:
        ni = board.FindNet(net)
        for a, b in zip(pts, pts[1:]):
            tr = pcbnew.PCB_TRACK(board)
            tr.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
            tr.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
            tr.SetWidth(mm(width))
            tr.SetLayer(layers[layer])
            tr.SetNet(ni)
            board.Add(tr)
    for net, x, y in vias:
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        v.SetWidth(mm(VIA_D))
        v.SetDrill(mm(VIA_DRILL))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNet(board.FindNet(net))
        board.Add(v)
    pcbnew.SaveBoard(PCB, board)
    total = sum(math.dist(a, b) for _, _, _, p in wires for a, b in zip(p, p[1:]))
    print(f"imported {len(wires)} wires, {len(vias)} vias, total track length {total:.1f} mm")


def drc():
    os.makedirs(OUT, exist_ok=True)
    board = pcbnew.LoadBoard(PCB)
    report = os.path.join(OUT, "drc_report.txt")
    pcbnew.WriteDRCReport(board, report, pcbnew.EDA_UNITS_MILLIMETRES, True)
    print(open(report).read())


if __name__ == "__main__":
    {"place": place, "import": import_ses, "drc": drc}[sys.argv[1]]()
