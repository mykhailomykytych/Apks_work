#!/usr/bin/env bash
# Regenerates the whole lab 2 design from the GUID (requires KiCad 7+ with python module pcbnew).
set -euo pipefail
cd "$(dirname "$0")"
KPY=${KPY:-/usr/bin/python3}          # python that can "import pcbnew"
python3 tools/guid_design.py
python3 tools/gen_kicad.py kicad                       # symbols, footprints, schematic
$KPY tools/build_pcb.py place                           # outline, placement, nets
$KPY tools/route_pcb.py                                 # 2-layer A* routing
$KPY tools/build_pcb.py drc                             # DRC report -> out/drc_report.txt
mkdir -p out gerber
(cd kicad && kicad-cli sch export pdf -o ../out/schematic.pdf lab2_guid_pcb.kicad_sch)
(cd kicad && kicad-cli pcb export pdf --layers F.Cu,B.Cu,F.SilkS,Edge.Cuts --include-border-title -o ../out/pcb_layout.pdf lab2_guid_pcb.kicad_pcb)
(cd kicad && kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts --subtract-soldermask -o ../gerber/ lab2_guid_pcb.kicad_pcb)
(cd kicad && kicad-cli pcb export drill --format excellon --excellon-units mm --generate-map --map-format gerberx2 -o ../gerber/ lab2_guid_pcb.kicad_pcb)
grep -q "Found 0 DRC violations" out/drc_report.txt && grep -q "Found 0 unconnected pads" out/drc_report.txt
echo "DONE: DRC clean, Gerber files in gerber/"
