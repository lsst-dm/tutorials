#!/usr/bin/env python
# shaw@noao.edu  2014-Jun-04

import argparse
import os
import sys

def mkConfig(args):
    """Create andConfig configuration file. 
    """
    descr_text = 'Create andConfig python configuration snippet'
    parser = argparse.ArgumentParser(description=descr_text)
    parser.add_argument('outFile', help='Name of output configuration file')
    parser.add_argument('-f', '--Filters', default='ugriz', \
                        help='Names of filters')
    parser.add_argument('-t', '--Template', default='index-', \
                        help='Template for index file names')
    args = parser.parse_args()

    with open(args.outFile, 'w') as f:
        f.write('root.starGalaxyColumn = "%s"\n' % (""))
        filters = args.Filters
        f.write("filters = ('" + "', '".join(filters) + "')\n")
        f.write("root.magColumnMap = dict([(f,f+'_med') for f in filters])\n")
        f.write("root.magErrorColumnMap = dict([(f, f+'_err') for f in filters])\n")
        f.write("root.indexFiles = [\n")
        for filename in os.listdir("."):
            if args.Template in filename:
                f.write("    '" + filename + "',\n")
        f.write("    ]\n")


if __name__ == '__main__':
    mkConfig(sys.argv)

