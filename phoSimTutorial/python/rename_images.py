""" distributeFilesForiRODS
    Given a filename and a top level directory move a file to the
    correct file structure and create directories if necessary

    ajc@astro.washington.edu 4/6/2010
    """

import os
import sys
import shutil
import glob
from optparse import OptionParser

def parseFileName(fileName):
    """ Return the path to the file

    Expected filename format is imsim_85770141_f0_R01_S22_C17_E001.fits.gz
    """

    #remove directory structure and .fits 
    stubs = os.path.basename(fileName).partition(".")

    #map filter number to filter character
    filtmap = {"f0":"fu", "f1":"fg", "f2":"fr", "f3":"fi", "f4":"fz", "f5":"fy"}
    
    if stubs[0].startswith("lsst_a"):
        imageType, a, obshistid, filter, raft, sensor, channel, exposure = stubs[0].split("_")
        filter = filtmap[filter]
   	path = "raw/v%d-%s/%s/%s/%s/" % (int(obshistid),filter, exposure, raft, sensor)
        filename = "imsim_%d_%s_%s_%s_%s.fits.gz"%(int(obshistid),raft,sensor,channel,exposure)
    elif stubs[0].startswith("lsst_e"):
	imageType, e, obshistid, filter, raft, sensor, exposure = stubs[0].split("_")
   	filter = filtmap[filter]
        path = "eimage/v%d-%s/%s/%s/" % (int(obshistid),filter,exposure, raft)
        filename = "eimage_%s_%s_%s_%s.fits.gz"%(obshistid,raft,sensor,exposure)
    else:
       raise TypeError("Incorrect file name: %s" % fileName)
    
    return path, filename 

def distributeFilesForiRODs(topLevelDir, fileName):
    """Move an image file to the iRODS directory structure"""

    path,filename = parseFileName(fileName)
    
    # generate directories. Race condition can exist if the directory
    # is create between checking existance and makedirs
    dir =  os.path.join(topLevelDir,path)
    print dir
    if not os.path.isdir(dir):
        try:
            os.makedirs(dir)
        except OSError:
            pass

    # move file
    try:
        shutil.move(fileName, os.path.join(dir,filename))
        #print fileName, "->", os.path.join(dir,filename)
    except:
        raise OSError("Unable to move filename %s" % fileName)

def main():

    usage = "usage: %prog toplevelDir filename (or wildcard)"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    try:
        topLevelDir = args[0]
        # assume that system will expand wild cards into the args list
        for fileName in args[1:]:
            print fileName
            distributeFilesForiRODs(topLevelDir, fileName)
    except ValueError, (ErrorMessage):
        print "Parse Error %s" % ErrorMessage
    except OSError, (ErrorMessage):
        print "IO Error %s", ErrorMessage
    except IndexError, (ErrorMessage):
        print "IndexError: USAGE distributeFilesForiRODS toplevelDir filename (or wildcard)"
        
if __name__ == '__main__':
    main()
