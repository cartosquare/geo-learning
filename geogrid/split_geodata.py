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
from __future__ import division
import os
import argparse
import multiprocessing
from mesher import Mesher
import grid_data_pb2
from progressbar import *


def parse_commandline():
    parser = argparse.ArgumentParser(description='Feed data to grid.')
    parser.add_argument('src', metavar='SRC', type=str, help='source data file to feed')
    parser.add_argument('--src_format', dest='format', type=str, help='data file format')
    parser.add_argument('--res', dest='resolution', type=int, help='resolution level from 1 to 19')
    parser.add_argument('--srs', dest='srs', type=str, help='coordinate system, can be epsg:3857 or epsg:4326')
    parser.add_argument('--output', dest='output', type=str, help='output directory')
    parser.add_argument('--out_format', dest='output_format', type=str, help='output format, can be directory or sqlite3')
    parser.add_argument('--ilayer', dest='ilayer', type=int, help='data layer index')
    parser.add_argument('--layer', dest='layer', type=str, help='data layer name')
    parser.add_argument('--filter', dest='filter', type=str, help='data layer filter')
    parser.add_argument('--method', dest='method', type=str, help='method to get grid value')
    parser.add_argument('--count_key', dest='cell_value', type=int, help='raster method operator')
    parser.add_argument('--threads', dest='nthreads', type=int, help='number of threads')
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
        args.method = 'sum'

    if args.nthreads == None:
        args.nthreads = 1

    if (args.method == 'count' or args.method == 'frequency') and args.cell_value is None:
        print 'You must specify -v option when using %s method!' % (args.method)
        return args, False

    if args.output_format != 'directory' and args.nthreads > 1:
        print 'multiprocessing must use directory output!'
        return args, False

    return args, True


def start_process():
    process_name = multiprocessing.current_process().name
    layers[process_name] = mesher.openLayer(args)


def paralle_jobs(k):
    process_name = multiprocessing.current_process().name
    layer = layers[process_name]
    mesher.makeGrid(k, layer)


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

    mesher.updateMetas()

    if args.nthreads > 1:
        layers = {}
        # progress bar
        widgets = [Bar('>'), ' ', Percentage(), ' ', Timer(), ' ', ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=len(mesher.grids.grid_list)).start()

        max_pool_size = multiprocessing.cpu_count() * 2
        if args.nthreads > max_pool_size:
            args.nthreads = max_pool_size
        print '#processing pool', args.nthreads
    
        pool = multiprocessing.Pool(processes=args.nthreads, initializer=start_process,)

        for i, _ in enumerate(pool.imap_unordered(paralle_jobs, mesher.grids.grid_list), 1):
            pbar.update(i)

        pool.close()
        pool.join()
        pbar.finish()
    else:
        mesher.make()