#!/usr/bin/env python
# shaw@noao.edu  2014-Apr-17

import sys

def genRetrieveList(inFname, outFname):
    """Reformat the list of camcol/field/filter/rerun/run to image URLs to retrieve with wget
    """

    inF  = open(inFname, 'r')
    outF = open(outFname, 'w')

    imageURLbase  = "http://das.sdss.org/imaging/"
    astromURLbase = "%d/%d/astrom/"
    corrBase      = "%d/%d/corr/%d/fpC-%06d-%s%d-%04d.fit.gz"           # fpC
    calibBase     = "%d/%d/calibChunks/%d/tsField-%06d-%d-%d-%04d.fit"  # tsField
    objcsBase1    = "%d/%d/objcs/%d/fpM-%06d-%s%d-%04d.fit"             # fpM
    objcsBase2    = "%d/%d/objcs/%d/psField-%06d-%d-%04d.fit"           # psField

    for line in inF:
        ad = {}
        for field in line.split()[1:]:   # Need to omit the prepended '--id '
            k,v = field.split('=')
            ad.update({k: v})
        run    = int(ad['run'])
        rerun  = int(ad['rerun'])
        camcol = int(ad['camcol'])
        sdss_field = int(ad['field'])
        astrom  = imageURLbase+astromURLbase % (run,rerun)
        corr    = imageURLbase+corrBase   % (run,rerun,camcol, run,ad['filter'],camcol,sdss_field)
        calib   = imageURLbase+calibBase  % (run,rerun,camcol, run,camcol,rerun,sdss_field)
        fpM     = imageURLbase+objcsBase1 % (run,rerun,camcol, run,ad['filter'],camcol,sdss_field)
        psField = imageURLbase+objcsBase2 % (run,rerun,camcol, run,camcol,sdss_field)

        outF.write(astrom+'\n')
        outF.write(calib+'\n')
        outF.write(corr+'\n')
        outF.write(fpM+'\n')
        outF.write(psField+'\n')
    inF.close()
    outF.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: genRetrieveList.py inFile.txt outFile.txt"
    else:
        genRetrieveList(sys.argv[1], sys.argv[2])

