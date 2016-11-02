# coding=utf8
import os
import sys
from osgeo import ogr
from osgeo import gdal
from grid import Grid
import grid_data_pb2
import sqlite3
import argparse
import numpy
gdal.UseExceptions()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Feed data to grid.')
    parser.add_argument('src', metavar='SRC', type=str, help='source data file to feed')
    parser.add_argument('-f', dest='format', type=str, help='data file format')
    parser.add_argument('-r', dest='resolution', type=str, help='resolution r1-r4')
    parser.add_argument('-o', dest='output', type=str, help='output directory')
    parser.add_argument('-n', dest='name', type=str, help='layer name')
    parser.add_argument('-b', dest='band', type=int, help='raster band')
    parser.add_argument('--xmin', dest='xmin', type=float, help="x min")
    parser.add_argument('--xmax', dest='xmax', type=float, help="x max")
    parser.add_argument('--ymin', dest='ymin', type=float, help="y min")
    parser.add_argument('--ymax', dest='ymax', type=float, help="y max")

    # parse arguments
    args = parser.parse_args()
    print args

    data_file = args.src
    data_format = args.format
    resolution = args.resolution
    output_dir = args.output
    layer_name = args.name
    band = args.band
    
    # open leveldb
    db_path = os.path.join(output_dir, layer_name)
    # will create if db not exists
    db = sqlite3.connect(db_path + '.sqlite3')
    db.execute('''CREATE TABLE IF NOT EXISTS feature
       (ID CHAR(50) PRIMARY KEY  NOT NULL,
       DATA           BLOB    NOT NULL);''')

    if band == None:
        # open vector layer
        driver = ogr.GetDriverByName(data_format)
        if driver is None:
            print "%s driver not available.\n" % data_format
            exit(0)

        # open data file read-only
        datasource = driver.Open(data_file, 0)
        if datasource is None:
            print 'could not open %s' % (data_file)
            exit(0)

        layer = datasource.GetLayer(layer_name)
        feature_count = layer.GetFeatureCount()
        print "number of features in %s: %d" % (os.path.basename(data_file), feature_count)

        # fetch layer extent
        extent = layer.GetExtent()
        print "layer extent minx: %f, maxx: %f, miny: %f, maxy: %f" % (extent[0], extent[1], extent[2], extent[3])
    else:
        # open raster layer
        try:
            datasource = gdal.Open(data_file)
        except RuntimeError, e:
            print 'Unable to open %s' % (data_file)
            print e
            sys.exit(1)

        geo_transform = datasource.GetGeoTransform()
        extent = [geo_transform[0], geo_transform[0] + geo_transform[1] * datasource.RasterXSize, geo_transform[3] + geo_transform[5] * datasource.RasterYSize, geo_transform[3]]
        print extent

        try:
            layer = datasource.GetRasterBand(band)
        except RuntimeError, e:
            print 'Band ( %i ) not found' % band
            print e
            sys.exit(1)

        layer = datasource.GetRasterBand(band)
        # print datasource.GetMetadata()
        
        stats = layer.GetStatistics(True, True)
        if stats is not None:
            print "[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])

    # update extent if specied
    extent = [extent[0] if args.xmin is None else args.xmin, extent[1] if args.xmax is None else args.xmax, extent[2] if args.ymin is None else args.ymin, extent[3] if args.ymax is None else args.ymax]

    # calculate grids
    grids = Grid(resolution, extent[0], extent[1], extent[2], extent[3])
    total_grids = grids.total_grids * grids.grid_size * grids.grid_size
    print "total grids: %d, %d" % (grids.total_grids, total_grids)

    cnt = 0
    step = total_grids / 1000
    if step <= 0:
        step = 1

    min = 1000000
    max = -min
    for k in grids.grid_list:
        # protobuf format grid data
        grid_data = grid_data_pb2.GridData()
        grid_data.name = resolution + '-' + k
        
        grid_layer = grid_data.layers.add()
        grid_layer.version = 2
        grid_layer.name = layer_name

        ext = grids.grid_list[k]

        count = 0
        for row in range(0, grids.grid_size):
            for col in range(0, grids.grid_size):
                # grid_layer.keys.append(row * grids.grid_size + col)

                xx = ext[0] + row * grids.res
                yy = ext[3] - col * grids.res

                extent = [xx, xx + grids.res, yy - grids.res, yy]

                if band is None:
                    # statistic for vector layer
                    # Create a Polygon from the extent tuple
                    ring = ogr.Geometry(ogr.wkbLinearRing)
                    ring.AddPoint(extent[0],extent[2])
                    ring.AddPoint(extent[1], extent[2])
                    ring.AddPoint(extent[1], extent[3])
                    ring.AddPoint(extent[0], extent[3])
                    ring.AddPoint(extent[0],extent[2])
                    poly = ogr.Geometry(ogr.wkbPolygon)
                    poly.AddGeometry(ring)

                    layer.SetSpatialFilter(None)
                    layer.SetSpatialFilter(poly)

                    grid_val = 0
                    # calculate count/length/area/.../ of the features in filtered layer
                    for feature in layer:
                        geom = feature.geometry()
                        geometry_type = geom.GetGeometryType()

                        if geometry_type == ogr.wkbPoint or geometry_type == ogr.wkbMultiPoint:
                            grid_val = grid_val + 1
                        elif geometry_type == ogr.wkbLineString or geometry_type == ogr.wkbMultiLineString:
                            grid_val = grid_val + geom.Length()
                        elif geometry_type == ogr.wkbPolygon or geometry_type == ogr.wkbMultiPolygon:
                            grid_val = grid_val + geom.GetArea()
                        else:
                            print 'unknow geometry type: %s' % (geometry_type)
                else:
                    # statistic for raster layer
                    x_offset = int((extent[0] - geo_transform[0]) / geo_transform[1])
                    y_offset = int((extent[3] - geo_transform[3]) / geo_transform[5])
                    x_size = int((extent[1] - extent[0]) / geo_transform[1] + 0.5)
                    y_size = int((extent[2] - extent[3]) / geo_transform[5] + 0.5)
                    data = layer.ReadAsArray(x_offset, y_offset, x_size, y_size)
                    if data is None:
                        grid_val = 0
                    else:
                        data = data.astype(numpy.float)
                        grid_val = numpy.average(data)
                    # print x_offset, y_offset, x_size, y_size, grid_val

                # find whether this grid value is already recorded
                target = -1
                for i in range(0, len(grid_layer.values)):
                    if abs(grid_val - grid_layer.values[i]) < 0.00001:
                        target = i

                if target == -1:
                    grid_layer.keys.append(len(grid_layer.values))
                    grid_layer.values.append(grid_val)
                else:
                    grid_layer.keys.append(target)

                # update min/max
                if min > grid_val:
                    min = grid_val
                if max < grid_val:
                    max = grid_val

                cnt = cnt + 1
                if (cnt % step == 0):
                    print 'Processed %.2f%%' % (100 * (float(cnt) / float(total_grids)))

        '''
        cnt = 0
        for key in grid_layer.keys:
            cnt = cnt + grid_layer.values[key]
        print cnt
        '''

        # save to db
        proto_str = grid_data.SerializeToString()
        db.execute('INSERT INTO feature(ID, DATA) VALUES(?, ?);', (grid_data.name, sqlite3.Binary(proto_str)))
    
    db.commit()