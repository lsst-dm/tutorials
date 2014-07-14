#!/usr/bin/env python
# shaw@noao.edu 2014-May-14

import argparse
import csv
import sys

import numpy as np
import pyfits

# Supported formats in FITS Binary tables, excepting complex types and array descriptors.
FORMAT_MAP = {'A':np.str, 'L':np.bool_, 'B':np.int8, 'I':np.int16, 'J':np.int32, 'K':np.int64, 'E':np.float32, 'D':np.float64}

def calCat2Fits(args):
    """Reformat an ASCII Star catalog to FITS BINTABLE, optionally adding an index column,
       and saving rows prepended by '#' to COMMENT cards in the primary header. 
       TBD: add option to omit selected columns from output. 
    """

    descr_text = 'Transform an ASCII Star Catalog to FITS format'
    parser = argparse.ArgumentParser(description=descr_text)
    parser.add_argument('inFile',  help='Name of input catalog file')
    parser.add_argument('cdFile',  help='Name of column definition file')
    parser.add_argument('outFile', help='Name of output FITS file')
    parser.add_argument('-c', '--Comments', action='store_true', \
                        help='Put #commented input rows into output primary header')
    parser.add_argument('-i', '--Index', action='store_true', \
                        help='Add column for row index')
#    parser.add_argument('-o', '--OmitCols', nargs='*', \
#                        help='List of column names to omit')
    args = parser.parse_args()

    # Fetch column definitions.
    rowList = []
    with open(args.cdFile, 'r') as cdFile:
        for row in csv.DictReader(cdFile, delimiter=','):
            rowList.append(row)

    nameList = [row['TTYPE'].strip() for row in rowList]
    formList = [row['TFORM'].strip() for row in rowList]
    dispList = [row['TDISP'].strip() for row in rowList]
    unitList = [row['TUNIT'].strip() for row in rowList]

    # Populate the catalog object
    cat = Catalog(nameList, formList)
    commentsList = []
    with open(args.inFile, 'r') as inFile:
        for line in csv.reader(inFile):
            fields = line[0].split()
            if fields[0].startswith('#'):
                commentsList.append(line[0].replace('#', ''))
            else:
                cat.append(fields)

    # Create the output table extension.
    if args.Index:
        colDefList = [pyfits.Column(name="ID", format='J', disp='I7', unit="", \
                      array=np.arange(1, cat.nRows+1, dtype=np.int32))]
    else:
        colDefList = []
    for i in range(len(nameList)):
        name = nameList[i]
        colDefList.append(pyfits.Column(name=name, format=formList[i], disp=dispList[i], \
                          unit=unitList[i], array=cat.fetchArr(name)))

    tbhdu = pyfits.new_table(pyfits.ColDefs(colDefList))
    prihdr = pyfits.Header()

    # Add comments to primary header.
    if args.Comments:
        for comment in commentsList:
            prihdr['COMMENT'] = comment
    prihdu = pyfits.PrimaryHDU(header=prihdr)
    thduList = pyfits.HDUList([prihdu, tbhdu])
    thduList.writeto(args.outFile)


class Catalog(object):
    """Collection of table columns and arrays of values. 
    """

    def __init__(self, colNameList, colFormList):
        """Constructor"""

        self.nRows = 0
        self.nCols = len(colNameList)
        assert(self.nCols == len(colFormList))
        formatList = []
        for form in colFormList:
            formatList.append(form[0])
        colTypeList = map(lambda x: FORMAT_MAP[x], formatList)

        self.colList = [dict(Name=colNameList[i], dtype=colTypeList[i], colArr=[]) for i in range(self.nCols)]


    def append(self, valList):
        """Append one value to each allocated Array from a list of value dictionaries.
           A value dict consists of at least 'Name' and (str)'Value' fields.
        """
        for i in range(len(valList)):
            self.colList[i]['colArr'].append(valList[i])
        self.nRows += 1


    def fetchArr(self, name):
        """Return a numpy array, cast to the declared type for the named column.
        """
        column = next((item for item in self.colList if item["Name"] == name), None)
        return np.array(column['colArr'], dtype=column['dtype'])


    def printCat(self):
        for col in self.colList:
            print "Column name: %s; Datatype: %s" % (col['Name'], col['dtype'])
            print col['colArr']


if __name__ == '__main__':

    calCat2Fits(sys.argv)
