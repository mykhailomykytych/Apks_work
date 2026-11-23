"""Generate the KiCad 7 project for lab 2 from the GUID:

* guid_parts.kicad_sym   - schematic symbols U1..U5 and connector J1
* guid_parts.pretty/     - footprints with the exact body sizes (N x N mm)
* lab2_guid_pcb.kicad_sch - schematic with all connections (net labels)
* lab2_guid_pcb.kicad_pro, sym-lib-table, fp-lib-table

Run:  python3 tools/gen_kicad.py <output_dir>
"""
import os
import sys
import uuid as _uuid

sys.path.insert(0, os.path.dirname(__file__))
from guid_design import GUID, FULL_NAME, components, all_nets, nets  # noqa: E402

PROJECT = "lab2_guid_pcb"
LIB = "guid_parts"
NS = _uuid.uuid5(_uuid.NAMESPACE_URL, "lab2-guid-pcb/" + GUID)


def uid(*parts):
    """Deterministic UUID so that regeneration gives identical files."""
    return str(_uuid.uuid5(NS, "/".join(str(p) for p in parts)))


def fnum(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ----------------------------------------------------------------------------
# Footprints
# ----------------------------------------------------------------------------
PAD_D, DRILL = 1.6, 0.9


def ic_pad_positions(n, side):
    """Pads on the body edge, QFP-like numbering (counter-clockwise from top-left)."""
    per = n // 4
    pitch = side / (per + 1)
    offs = [(k - (per - 1) / 2) * pitch for k in range(per)]
    h = side / 2
    pos = []
    pos += [(-h, o) for o in offs]               # left side, top -> bottom
    pos += [(o, h) for o in offs]                # bottom, left -> right
    pos += [(h, -o) for o in offs]               # right, bottom -> top
    pos += [(-o, -h) for o in offs]              # top, right -> left
    return pos


def fp_name(ref, side):
    return f"GUID_{ref}_{side}x{side}mm" if ref != "J1" else "GUID_J1_1x04_P2.54mm"


def footprint_ic(ref, chars, side):
    name = fp_name(ref, side)
    h = side / 2
    c = h + PAD_D / 2 + 0.25                      # courtyard half-size
    s = h + PAD_D / 2 + 0.15                      # silkscreen outline (outside pads)
    lines = [
        f'(footprint "{name}" (version 20221018) (generator pcbnew)',
        '  (layer "F.Cu")',
        f'  (descr "Square component {ref}: GUID group {chars}, {side}x{side} mm body, {len(chars)} pins")',
        '  (attr through_hole)',
        f'  (fp_text reference "REF**" (at 0 {fnum(-c - 1.2)}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        f'  (fp_text value "{name}" (at 0 {fnum(c + 1.2)}) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        f'  (fp_text user "{chars}" (at 0 0) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        f'  (fp_rect (start {fnum(-h)} {fnum(-h)}) (end {fnum(h)} {fnum(h)}) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))',
        f'  (fp_rect (start {fnum(-s)} {fnum(-s)}) (end {fnum(s)} {fnum(s)}) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))',
        f'  (fp_circle (center {fnum(-s - 0.6)} {fnum(-s - 0.6)}) (end {fnum(-s - 0.3)} {fnum(-s - 0.6)}) (stroke (width 0.3) (type solid)) (fill solid) (layer "F.SilkS"))',
        f'  (fp_rect (start {fnum(-c)} {fnum(-c)}) (end {fnum(c)} {fnum(c)}) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))',
    ]
    for i, (x, y) in enumerate(ic_pad_positions(len(chars), side), 1):
        shape = "rect" if i == 1 else "circle"
        lines.append(
            f'  (pad "{i}" thru_hole {shape} (at {fnum(x)} {fnum(y)}) (size {PAD_D} {PAD_D}) (drill {DRILL}) (layers "*.Cu" "*.Mask"))'
        )
    lines.append(")")
    return name, "\n".join(lines) + "\n"


def footprint_conn(n=4):
    name = fp_name("J1", 0)
    p = 2.54
    y0 = -(n - 1) * p / 2
    lines = [
        f'(footprint "{name}" (version 20221018) (generator pcbnew)',
        '  (layer "F.Cu")',
        '  (descr "Edge connector for free GUID pins, 1x04, pitch 2.54 mm")',
        '  (attr through_hole)',
        f'  (fp_text reference "REF**" (at 0 {fnum(y0 - 2.6)}) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
        f'  (fp_text value "{name}" (at 0 {fnum(-y0 + 2.6)}) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',
        f'  (fp_rect (start -1.27 {fnum(y0 - 1.27)}) (end 1.27 {fnum(-y0 + 1.27)}) (stroke (width 0.1) (type solid)) (fill none) (layer "F.Fab"))',
        f'  (fp_rect (start -1.4 {fnum(y0 - 1.4)}) (end 1.4 {fnum(-y0 + 1.4)}) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))',
        f'  (fp_rect (start -1.8 {fnum(y0 - 1.8)}) (end 1.8 {fnum(-y0 + 1.8)}) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))',
    ]
    for i in range(n):
        shape = "rect" if i == 0 else "circle"
        lines.append(
            f'  (pad "{i + 1}" thru_hole {shape} (at 0 {fnum(y0 + i * p)}) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask"))'
        )
    lines.append(")")
    return name, "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------
# Symbols
# ----------------------------------------------------------------------------
G = 2.54


def symbol_pins(n):
    """Pin connection points in symbol coordinates (y up). Left: 1..L, right: L+1..n."""
    left = (n + 1) // 2
    right = n - left
    rows = max(left, right)
    top = (rows - 1) * G / 2
    pins = []
    for k in range(left):
        pins.append((-7.62, top - k * G, 0))
    for k in range(right):
        pins.append((7.62, top - k * G, 180))
    return pins, (rows + 1) * G / 2


def symbol_def(name, ref_prefix, footprint, pin_names, value, conn=False):
    n = len(pin_names)
    if conn:
        pins = [(5.08, (n - 1) * G / 2 - k * G, 180) for k in range(n)]
        half_h = (n + 1) * G / 2
        rect = f"(rectangle (start -2.54 {fnum(half_h)}) (end 2.54 {fnum(-half_h)})"
    else:
        pins, half_h = symbol_pins(n)
        rect = f"(rectangle (start -5.08 {fnum(half_h)}) (end 5.08 {fnum(-half_h)})"
    out = [
        f'    (symbol "{name}" (in_bom yes) (on_board yes)',
        f'      (property "Reference" "{ref_prefix}" (at 0 {fnum(half_h + 1.27)} 0) (effects (font (size 1.27 1.27))))',
        f'      (property "Value" "{value}" (at 0 {fnum(-half_h - 1.27)} 0) (effects (font (size 1.27 1.27))))',
        f'      (property "Footprint" "{footprint}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        '      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
        f'      (symbol "{name.split(":")[-1]}_0_1"',
        f'        {rect} (stroke (width 0.254) (type default)) (fill (type background)))',
        "      )",
        f'      (symbol "{name.split(":")[-1]}_1_1"',
    ]
    for i, ((x, y, a), pname) in enumerate(zip(pins, pin_names), 1):
        out.append(
            f'        (pin passive line (at {fnum(x)} {fnum(y)} {a}) (length 2.54)'
            f' (name "{pname}" (effects (font (size 1.27 1.27)))) (number "{i}" (effects (font (size 1.27 1.27)))))'
        )
    out += ["      )", "    )"]
    return "\n".join(out), pins


def part_list():
    parts = []
    for ref, chars, side in components():
        parts.append(dict(ref=ref, sym=f"GUID_{ref}", fp=f"{LIB}:{fp_name(ref, side)}",
                          pins=list(chars), value=f"{ref} '{chars}' {side}x{side}mm", conn=False))
    _, free = nets()
    parts.append(dict(ref="J1", sym="GUID_J1_EDGE", fp=f"{LIB}:{fp_name('J1', 0)}",
                      pins=[f"{ch}" for ch, _, _ in free], value="Edge 1x04 (free pins)", conn=True))
    return parts


# Schematic placement (mm, schematic coordinates: y down)
SCH_POS = {"J1": (40.64, 101.6), "U1": (101.6, 63.5), "U2": (101.6, 139.7),
           "U3": (177.8, 63.5), "U4": (177.8, 139.7), "U5": (241.3, 101.6)}


def write_schematic(path, parts, sym_defs):
    root = uid("root")
    pin_net = {}
    for net, pins in all_nets().items():
        for ref, p in pins:
            pin_net[(ref, p)] = net

    out = [
        f'(kicad_sch (version 20230121) (generator eeschema)',
        f'  (uuid {root})',
        '  (paper "A4")',
        '  (title_block',
        '    (title "Lab 2: GUID-based PCB (credit card form factor)")',
        '    (date "2026-11-23")',
        '    (rev "1")',
        f'    (comment 1 "GUID: {GUID}")',
        f'    (comment 2 "{FULL_NAME}, KI-407")',
        '  )',
        '  (lib_symbols',
    ]
    for p in parts:
        out.append(sym_defs[p["ref"]][0])
    out.append("  )")

    for p in parts:
        ref = p["ref"]
        sx, sy = SCH_POS[ref]
        _, pins = sym_defs[ref]
        half_h = (max((len(p["pins"]) + 1) // 2, len(p["pins"]) // 2) + 1) * G / 2 if not p["conn"] else (len(p["pins"]) + 1) * G / 2
        out.append(
            f'  (symbol (lib_id "{LIB}:{p["sym"]}") (at {fnum(sx)} {fnum(sy)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)'
        )
        out.append(f'    (uuid {uid("sym", ref)})')
        out.append(f'    (property "Reference" "{ref}" (at {fnum(sx)} {fnum(sy - half_h - 1.27)} 0) (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Value" "{p["value"]}" (at {fnum(sx)} {fnum(sy + half_h + 1.27)} 0) (effects (font (size 1.27 1.27))))')
        out.append(f'    (property "Footprint" "{p["fp"]}" (at {fnum(sx)} {fnum(sy)} 0) (effects (font (size 1.27 1.27)) hide))')
        out.append(f'    (property "Datasheet" "" (at {fnum(sx)} {fnum(sy)} 0) (effects (font (size 1.27 1.27)) hide))')
        for i in range(1, len(p["pins"]) + 1):
            out.append(f'    (pin "{i}" (uuid {uid("pin", ref, i)}))')
        out.append(f'    (instances (project "{PROJECT}" (path "/{root}" (reference "{ref}") (unit 1))))')
        out.append("  )")

        # wire stub + net label for every pin
        for i, (px, py, a) in enumerate(pins, 1):
            x0, y0 = sx + px, sy - py
            d = -1 if a == 0 else 1          # left pins extend to the left
            x1 = x0 + d * 5.08
            net = pin_net.get((ref, i))
            out.append(
                f'  (wire (pts (xy {fnum(x0)} {fnum(y0)}) (xy {fnum(x1)} {fnum(y0)})) (stroke (width 0) (type default)) (uuid {uid("w", ref, i)}))'
            )
            if net:
                ang, just = (180, "right bottom") if d < 0 else (0, "left bottom")
                out.append(
                    f'  (label "{net}" (at {fnum(x1)} {fnum(y0)} {ang}) (fields_autoplaced) (effects (font (size 1.27 1.27)) (justify {just})) (uuid {uid("l", ref, i)}))'
                )
            else:
                out.append(f'  (no_connect (at {fnum(x1)} {fnum(y0)}) (uuid {uid("nc", ref, i)}))')

    out.append(
        f'  (text "GUID {GUID} = {FULL_NAME}\\nU1..U5: group length = side (mm) = number of pins; pin name = GUID character.\\n'
        f'Pins with the same character are connected (net N_<char>). Characters that occur once are free pins,\\n'
        f'routed to edge connector J1 on the short side of the board (nets FREE_<char>)." '
        f'(at 25.4 172.72 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uid("note")}))'
    )
    out.append('  (sheet_instances (path "/" (page "1")))')
    out.append(")")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


def main(outdir):
    os.makedirs(os.path.join(outdir, f"{LIB}.pretty"), exist_ok=True)
    parts = part_list()

    # footprints
    for ref, chars, side in components():
        name, text = footprint_ic(ref, chars, side)
        with open(os.path.join(outdir, f"{LIB}.pretty", name + ".kicad_mod"), "w") as fh:
            fh.write(text)
    name, text = footprint_conn(len(parts[-1]["pins"]))
    with open(os.path.join(outdir, f"{LIB}.pretty", name + ".kicad_mod"), "w") as fh:
        fh.write(text)

    # symbols: library file + definitions embedded into the schematic
    sym_defs, lib_body = {}, []
    for p in parts:
        lib_text, pins = symbol_def(p["sym"], "J" if p["conn"] else "U", p["fp"], p["pins"], p["value"], p["conn"])
        lib_body.append(lib_text)
        emb_text, _ = symbol_def(f'{LIB}:{p["sym"]}', "J" if p["conn"] else "U", p["fp"], p["pins"], p["value"], p["conn"])
        sym_defs[p["ref"]] = (emb_text, pins)
    with open(os.path.join(outdir, f"{LIB}.kicad_sym"), "w") as fh:
        fh.write("(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n")
        fh.write("\n".join(lib_body) + "\n)\n")

    write_schematic(os.path.join(outdir, f"{PROJECT}.kicad_sch"), parts, sym_defs)

    with open(os.path.join(outdir, "sym-lib-table"), "w") as fh:
        fh.write(f'(sym_lib_table\n  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.kicad_sym")(options "")(descr "GUID parts"))\n)\n')
    with open(os.path.join(outdir, "fp-lib-table"), "w") as fh:
        fh.write(f'(fp_lib_table\n  (lib (name "{LIB}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIB}.pretty")(options "")(descr "GUID footprints"))\n)\n')
    pro = os.path.join(outdir, f"{PROJECT}.kicad_pro")
    if not os.path.exists(pro):
        with open(pro, "w") as fh:
            fh.write('{\n  "meta": {\n    "filename": "%s.kicad_pro",\n    "version": 1\n  }\n}\n' % PROJECT)
    print("generated KiCad project in", outdir)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "kicad")
