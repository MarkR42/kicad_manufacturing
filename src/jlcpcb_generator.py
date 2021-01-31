#!/usr/bin/env python3
import sexpdata
from sexpdata import Symbol
import os
import sys
import collections
import re

Footprint = collections.namedtuple('Footprint',
    ['footprint', 'layer', 'at', 'reference', 'value', 'lcsc',
        'unique_reference']
        )

seen_references = set()

def split_reference(ref):
    # Return two parts - the first part, and the number
    alpha =  ''
    num = ''
    for c in ref:
        if c.isdigit():
            num += c
        else:
            alpha += c
    return alpha, num

def make_unique_reference(ref):
    if ref in seen_references:
        # Handle non-unique case
        alpha, num = split_reference(ref)
        try:
            num = int(num)
        except ValueError:
            num = 1
        for increment in range(100,5000,100):
            unique_ref = alpha + str(num + increment)
            if unique_ref not in seen_references:
                # Found unique.
                break
        if unique_ref in seen_references:
            raise Exception("Failed to create unique reference for " + ref)
    else:
        unique_ref = ref
    seen_references.add(unique_ref)
    return unique_ref

def find_child_symbols(kids, symbol_name):
    want_symbol = Symbol(symbol_name)
    return list(
        filter(lambda n: n[0] == want_symbol, kids)
    )

def handle_footprint(fp):
    # Footprint name - inti
    footprint = fp[1]
    # Find layer
    # print(fp)
    layer = find_child_symbols(fp, 'layer')[0][1]
    # coordinate.
    at = find_child_symbols(fp, 'at')[0][1:]
    # text items
    text_items = {}
    for fp_text in find_child_symbols(fp, 'fp_text'):
        text_items[str(fp_text[1])] = fp_text[2]
    reference = text_items.get('reference', '?')
    value = text_items.get('value', '?')
    # properties
    properties = {}
    for prop in find_child_symbols(fp, 'property'):
        properties[str(prop[1])] = prop[2]
    lcsc = properties.get('LCSC', '')
    unique_reference = make_unique_reference(reference)
    if lcsc == '':
        # No lcsc part number
        return None
    
    print("ref: {} unique: {} footprint: {} value: {} layer: {} at: {} LCSC: {}".format(
        reference, unique_reference, 
        footprint, value, layer, repr(at), lcsc))
    fptuple = Footprint(
        footprint, layer, at, reference, value, lcsc, unique_reference)
    return fptuple

def write_bom(fptuples):
    # Find distinct set of parts.
    parts = set()
    bom_groups = collections.defaultdict(list)
    for fp in fptuples:
        parts.add(fp.lcsc)
        bom_groups[fp.lcsc].append(fp)
    
    with open('jlc_bom.csv','wt') as f:
        print("Comment,Designator,Footprint,LCSC", file=f)
        for part in parts:
            firstpart = bom_groups[part][0]
            comment = firstpart.value
            footprint = firstpart.footprint
            ref_list = ','.join([fp.unique_reference for fp in bom_groups[part]])
            print('{},"{}",{},{}'.format(
                comment, ref_list, footprint, part),
                file=f)

def write_pos(fptuples, rotations):
    # Write the jlc position file.
    with open('jlc_pos.csv','wt') as f:
        print('"Designator","Mid X","Mid Y","Layer","Rotation"', file=f)
        for fp in fptuples:
            rotation = get_part_rotation(rotations, fp.footprint)
            x = fp.at[0]
            y = - fp.at[1]
            rot = 0
            if len(fp.at)>2:
                rot = fp.at[2]
            rot += rotation
            layer = 'Top'
            if fp.layer.startswith('B'):
                layer='Bottom'
            print('"{}","{}","{}","{}","{}"'.format(
                fp.unique_reference, x,y, layer, rot
                ),
                file=f)

def handle_doc(doc, rotations):
    # Find all footprint objects...
    fptuples = []
    for n in find_child_symbols(doc, 'footprint'):
        fp = handle_footprint(n)
        if fp:
            fptuples.append(fp)
    write_bom(fptuples)
    write_pos(fptuples, rotations)
    
    
def get_part_rotation(rotations, footprint):
    # Footprint can be, for example:
    # Package_TO_SOT_SMD:SOT-23
    # Ignore the first part.
    footprint = footprint.split(':')[-1]
    found_rotation = 0
    for exp, rotation in rotations:
        if re.search(exp, footprint, re.IGNORECASE):
            found_rotation = rotation
            break
    return found_rotation
    
def load_rotations():
    """
        Return a list of tuples (regex, rotation)
    """
    fn = os.path.join(os.path.dirname(__file__), 'rotations.cf')
    rotations = []
    with open(fn, 'rt') as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                if not line.startswith('#'):
                    bits = line.split()
                    if len(bits) >= 2:
                        exp = bits[0]
                        rotation = int(bits[1])
                        rotations.append( (exp, rotation) )
    print("Rotations loaded: {}".format(len(rotations)))
    return rotations

def main():
    rotations = load_rotations()
    if len(sys.argv) <2:
        print("Please supply filename on command line")
        raise Exception("No filename")
    filename = sys.argv[1]
    with open(filename) as f:
        doc = sexpdata.load(f)

    file_dir = os.path.dirname(filename)
    if len(file_dir) > 0:
        os.chdir(os.path.dirname(filename))
    handle_doc(doc, rotations)

if __name__ == '__main__':
    main()
