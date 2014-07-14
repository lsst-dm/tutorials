#!/usr/bin/env python
# shaw@noao.edu  2014-Jun-06

import argparse
import csv
import re
import sys

import numpy as np
import lsst.daf.persistence as dafPersist
from lsst.obs.lsstSim import LsstSimMapper
from lsst.afw.geom import Angle

DEFAULT_COLS = (
    "id", 
    "coord.ra",
    "coord.dec",
    "flags.negative",
    "flags.badcentroid",
    "flags.pixel.edge",
    "flags.pixel.interpolated.any",
    "flags.pixel.interpolated.center",
    "flags.pixel.saturated.any",
    "flags.pixel.saturated.center",
    "centroid.sdss.x",
    "centroid.sdss.y",
    "centroid.sdss.err.xx",
    "centroid.sdss.err.yy",
    "shape.sdss.xx",
    "shape.sdss.xy",
    "shape.sdss.yy",
    "shape.sdss.err.xx",
    "shape.sdss.err.xy",
    "shape.sdss.err.yy",
    "shape.sdss.flags",
    "flux.gaussian",
    "flux.gaussian.err",
    "flux.psf",
    "flux.psf.err",
    "flux.sinc",
    "flux.sinc.err",
    "classification.extendedness",
    "correctfluxes.apcorr",
    "correctfluxes.apcorr.flags",
    )

def makeCat(args):
    """Create merged catalog of sources from multiple tables."""

    descr_text = 'Create merged catalog of sources from multiple tables'
    parser = argparse.ArgumentParser(description=descr_text)
    parser.add_argument('repoDir', help='Name of repository directory')
    parser.add_argument('visits', help='Visit selector')
    parser.add_argument('-c', '--ColFile', help='File of space-separated columns of interest')
    args = parser.parse_args()

    visits = args.visits
    if args.ColFile is None:
        cols = DEFAULT_COLS
    else:
        with open(args.ColFile, 'rb') as f:
            # The file of column names should contain only one row.
            for row in csv.reader(f, delimiter=' '):
                cols = row

    print '#' + ' '.join(cols) + ' filter'

    butler = dafPersist.Butler(args.repoDir)
#    vList = [dict(visit=int(v)) for v in visits.split('^')]
    vList = []
    for v in visits.split("^"):
        mat = re.search(r"^(\d+)\.\.(\d+)(?::(\d+))?$", v)
        if mat:
            v1 = int(mat.group(1))
            v2 = int(mat.group(2))
            v3 = mat.group(3); v3 = int(v3) if v3 else 1
            for v in range(v1, v2 + 1, v3):
                vList.append(dict(visit=v))
        else:
            vList.append(dict(visit=int(v)))
    
    for dataId in (vList):
        if not butler.datasetExists("src", **dataId):
            continue

        srcs = butler.get("src", **dataId)
        filter = butler.queryMetadata("calexp", "filter", visit=dataId['visit'])[0]

        vecs = []
        for col in cols:
            if col.endswith(".ra") or col.endswith(".dec"):
                v = np.rad2deg(srcs.get(col))
            elif re.search(r"\.err\.(xx|yy|xy)$", col):
                field, which = re.search(r"^(.*\.err)\.(xx|yy|xy)$", col).groups()
                key = srcs.schema.find(field).key
                key = key[0,0] if which == "xx" else key[1,1] if which == "yy" else key[0, 1]

                v = srcs.get(key)
            else:
                v = srcs.get(col)

            vecs.append(v)

        for vals in zip(*vecs):
            print ' '.join([str(el) for el in vals]) + ' ' + filter

if __name__ == '__main__':
    makeCat(sys.argv)
