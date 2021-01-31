# kicad_manufacturing
A utility which export Kicad 6+ PCB files for specific manufacturers.

Based on https://github.com/essele/kicad_jlcpcba

How to use:

1. Design your schematic, and add the property "LCSC" to each part you want to place.

Use the LCSC part numbers shown in https://jlcpcb.com/parts

For example, C52923 is a 1uF 0402 capacitor.

Make sure that the footprint is correct for the part chosen.

2. Layout the board normally. Generate the gerber files, drill files etc, as required
by the manufacturer.

3. Run jlcpcb_generator.py on the .kicad_pcb file

If all goes well, it should generate jlc_bom.csv and jlc_pos.csv in the same directory.
Those files can be used by the assembly service to hopefully correctly
assemble the board.


