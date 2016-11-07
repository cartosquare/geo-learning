# -*- coding: utf-8 -*-

"""
/***************************************************************************
 split_geodata
                                 data dump script
 cut raster/vector data to grids
                              -------------------
        begin                : 2016-11-3
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""


import argparse
from mesher import Mesher

def parse_commandline():
    parser = argparse.ArgumentParser(description='Feed data to grid.')
    parser.add_argument('src', metavar='SRC', type=str, help='source data file to feed')
    parser.add_argument('-f', dest='format', type=str, help='data file format')
    parser.add_argument('-r', dest='resolution', type=str, help='resolution r1-r4')
    parser.add_argument('-o', dest='output', type=str, help='output path')
    parser.add_argument('-t', dest='output_format', type=str, help='output format, can be directory or sqlite3')
    parser.add_argument('-b', dest='ilayer', type=int, help='data layer index')
    parser.add_argument('-m', dest='method', type=str, help='method to get grid value')
    parser.add_argument('-v', dest='cell_value', type=int, help='raster method operator')
    parser.add_argument('--xmin', dest='xmin', type=float, help="x min")
    parser.add_argument('--xmax', dest='xmax', type=float, help="x max")
    parser.add_argument('--ymin', dest='ymin', type=float, help="y min")
    parser.add_argument('--ymax', dest='ymax', type=float, help="y max")

    # parse arguments
    args = parser.parse_args()
    if args.src is None:
        print 'You must specify data source and layer name!'
        return args, False

    if args.format is None:
        print 'You must specify data source format!'
        return args, False

    if args.resolution is None:
        args.resolutin = 'r3'

    if args.output is None:
        args.output = 'output'

    if args.output_format is None:
        args.output_format = 'directory'

    if args.format == 'GeoTiff':
        args.type = 'raster'
    else:
        args.type = 'vector'

    if args.ilayer is None and args.type == 'vector':
        args.ilayer = 0

    if args.ilayer is None and args.type == 'raster':
        args.ilayer = 1

    if args.method is None:
        args.method = 'count'

    if (args.method == 'count' or args.method == 'frequency') and args.cell_value is None:
        print 'You must specify -v option when using %s method!' % (args.method)
        return args, False

    return args, True


if __name__=='__main__':
    # parse command line parameters
    args, success = parse_commandline()
    if not success:
        exit(0)
    
    mesher = Mesher(args.resolution)
    
    if not mesher.openSource(args):
        exit(0)
    if not mesher.openDest(args):
        exit(0)

    mesher.make(args.method, args.cell_value)

    

    

    