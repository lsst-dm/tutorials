#!/usr/bin/env python
# shaw@noao.edu  2014-Jun-04

import argparse
import sys

RA_DEFAULT_LIMIT  = (-0.50, 0.50)
DEC_DEFAULT_LIMIT = (-0.50, 0.50)
SDSS_DEC_MAX = +1.25
SDSS_DEC_MIN = -1.25
NOBS_COL = {'u':7, 'g':13, 'r':19, 'i': 25, 'z':31}
MAGS_COL = {'u':8, 'g':14, 'r':20, 'i': 26, 'z':32}
FILTER_NUM = {'u':0, 'g':1, 'r':2, 'i': 3, 'z':4}

def refCalCat(args):
    """Reformat the SDSS Stripe 82 Standard Star catalog to be suitable for phoSim trim file.
    """

    descr_text = 'Transform SDSS Stripe 82 Standard Star Catalog to Trim file'
    parser = argparse.ArgumentParser(description=descr_text)
    parser.add_argument('inFile', help='Name of input catalog file')
    parser.add_argument('-f', '--filter', help='SDSS Filter', \
                        choices=['u','g','r','i','z'], default='r')
    parser.add_argument('-i', '--ID', type=int, default=1234567, \
                        help='Visit numeric identifier')
    parser.add_argument('-p', '--path', default='.', \
                        help='Path to SED library, relative to $PHOSIM_DIR/data/')
    parser.add_argument('--ralim', nargs=2, type=float, \
                        help='RA bounds (low high) in deg')
    parser.add_argument('--declim', nargs=2, type=float, \
                        help='Dec bounds (low high) in deg')
    args = parser.parse_args()

    # Output the PhoSim options prolog
    print "Opsim_obshistid %07d" % (args.ID)
    print "Opsim_rawseeing 0.65"            # Native seeing for this observation (arcsec)
    print "Opsim_filter %1s" % (FILTER_NUM[args.filter])
    print "SIM_NSNAP 1"                     # Number of snaps in this visit
    print "SIM_VISTIME 15.0"                # Duration of visit (s)

    ra_limits,dec_limits = setBounds(args.ralim, args.declim)

    objId = 0
    with open(args.inFile, 'r') as inF:
        for line in inF:
            if not line.startswith('###'):
                ls = line.split()
                ra  = float(ls[1])
                if ra > 180.:
                    ra -= 360.
                dec = float(ls[2])
                if inBox(ra, dec, ra_limits, dec_limits):
                    if (int(ls[NOBS_COL[args.filter]]) > 3):
                        objId += 1
                        print formOutput(ls, objId, args.filter, args.path)


def setBounds(ralim, declim):
    """Set RA, Dec boundaries, being mindful of wrapping at 0,360 degrees.
    """

    if ralim is None:
        raLimits = RA_DEFAULT_LIMIT
    else:
        if ralim[0] > 180.:
            ralim[0] -= 360.
        if ralim[1] > 180.:
            ralim[1] -= 360.
        raLimits = (min(ralim), max(ralim))

    if declim is None:
        decLimits = DEC_DEFAULT_LIMIT
    else:
        decLow  = max(min(declim), SDSS_DEC_MIN)
        decHigh = min(max(declim), SDSS_DEC_MAX)
        decLimits = (decLow, decHigh)

    return (raLimits, decLimits)


def inBox(ra, dec, RA_LIM, DEC_LIM):
    if RA_LIM[0] <= ra <= RA_LIM[1]:
        if DEC_LIM[0] <= dec <= DEC_LIM[1]:
            return True
    return False


def formOutput(pList, objId, filter, path):
    outStr = "object %5d %s %s %s %s/sed_flat.txt 0 0 0 0 0 0 star none none" % \
             (objId, pList[1], pList[2], pList[MAGS_COL[filter]], path)
    return outStr


if __name__ == '__main__':

    refCalCat(sys.argv)
