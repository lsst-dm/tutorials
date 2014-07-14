#!/usr/bin/env python
# shaw@noao.edu  2014-Apr-14

import sys

def refCoaddList(inFname):
    """Reformat the list of images to co-add, for processSdssCCd.py
    """

    inF  = open(inFname, 'r')

    for line in inF:
        if line.startswith('dataId='):
            print '--id ' + line.split(';')[0].replace('dataId=','')
    inF.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: refCoaddList inFile.txt > outFile.txt"
    else:
        refCoaddList(sys.argv[1])