#!/usr/bin/env python3
import sexpdata
from sexpdata import Symbol
import os
import sys

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
    print("ref: {} footprint: {} value: {} layer: {} at: {} LCSC: {}".format(reference, 
        footprint, value, layer, repr(at), lcsc))

def handle_doc(doc):
    # Find all footprint objects...
    for n in find_child_symbols(doc, 'footprint'):
        handle_footprint(n)

def main():
    if len(sys.argv) <2:
        print("Please supply filename on command line")
        raise Exception("No filename")
    with open(sys.argv[1]) as f:
        doc = sexpdata.load(f)
        handle_doc(doc)

if __name__ == '__main__':
    main()
