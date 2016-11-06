# -*- coding: utf-8 -*-

"""
/***************************************************************************
 vector_layer
                                 vector layer
 operation about vector layers
                              -------------------
        begin                : 2016-11-4
        copyright            : (C) 2016 by GeoHey
        email                : xux@geohey.com
 ***************************************************************************/
"""

import os
import sys
from osgeo import ogr

class VectorLayer:
    """VectorLayer Class"""
    def __init__(self):
        self.success = False

    def __del__(self):
        # clean
        self.datasource.Destroy()

    def open(self, src, ilayer, format):
        # open vector layer
        self.driver = ogr.GetDriverByName(format)
        if self.driver is None:
            print "%s driver not available.\n" % format
            self.success = False
            return self.success

        # open data file read-only
        self.datasource = self.driver.Open(src, 0)
        if self.datasource is None:
            print 'could not open %s' % (src)
            self.success = False
            return self.success

        self.layer = self.datasource.GetLayer(ilayer)
        self.feature_count = self.layer.GetFeatureCount()
        print "number of features in %s: %d" % (os.path.basename(src), self.feature_count)

        self.name = self.layer.GetName()

        # fetch layer extent
        self.extent = self.layer.GetExtent()
        print "layer[%s] extent minx: %f, maxx: %f, miny: %f, maxy: %f" % (self.name, self.extent[0], self.extent[1], self.extent[2], self.extent[3])

        self.success = True
        return self.success

    def spatialQuery(self, extent):
        if not self.success:
            print('layer is not opened correctly')
            return None

        # avoid nonsense query
        if extent[0] > self.extent[1] or extent[1] < self.extent[0] or extent[2] > self.extent[3] or extent[3] < self.extent[2]:
            return None

        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(extent[0],extent[2])
        ring.AddPoint(extent[1], extent[2])
        ring.AddPoint(extent[1], extent[3])
        ring.AddPoint(extent[0], extent[3])
        ring.AddPoint(extent[0],extent[2])
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        self.layer.SetSpatialFilter(None)
        self.layer.SetSpatialFilter(poly)
        return self.layer

    def statistic(self, extent):
        if not self.success:
            print('layer is not opened correctly')
            return

        data = self.spatialQuery(extent)
        if data is None:
            # extent has no intersection with this data, return right now
            return None
        else:
            grid_val = 0
            # calculate count/length/area/.../ of the features in filtered layer
            for feature in data:
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
            return grid_val

    