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
import json
from osgeo import ogr
import pyclipper


class VectorLayer:
    """VectorLayer Class"""
    def __init__(self):
        self.success = False

    def __del__(self):
        # clean
        self.datasource.Destroy()

    def setStatisticMethod(self, method, user_data):
        self.method = method
        self.user_data = user_data

    def open(self, src, ilayer, format, filter=None):
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
        if filter is not None:
            self.layer.SetAttributeFilter(filter)

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

    def toCoordinateArray(self, geom):
        geom.FlattenTo2D()
        return json.loads(geom.ExportToJson())['coordinates']

    def clipPolyline(self, clip, geom, geometry_type):
        pc = pyclipper.Pyclipper()
        try:
            pc.AddPath(clip, pyclipper.PT_CLIP, True)
        
            subject = self.toCoordinateArray(geom)
            if geometry_type == ogr.wkbLineString:
                pc.AddPath(subject, pyclipper.PT_SUBJECT, False)
            else:
                pc.AddPaths(subject, pyclipper.PT_SUBJECT, False)

            solution = pc.Execute2(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
            linestrigns = pyclipper.OpenPathsFromPolyTree(solution)
        except pyclipper.ClipperException as e:
            print 'Warning:', e, subject
            return None

        multiline_geom = ogr.Geometry(ogr.wkbMultiLineString)
        for line in linestrigns:
            line_geom = ogr.Geometry(ogr.wkbLineString)
            for pt in line:
                line_geom.AddPoint(pt[0], pt[1])
            multiline_geom.AddGeometry(line_geom)
        return multiline_geom


    def clipPolygon(self, clip, geom, geometry_type):
        pc = pyclipper.Pyclipper()
        try:
            pc.AddPath(clip, pyclipper.PT_CLIP, True)
        
            subject = self.toCoordinateArray(geom)
            pc.AddPaths(subject, pyclipper.PT_SUBJECT, True)

            solution = pc.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        except pyclipper.ClipperException as e:
            print 'Warning:', e
            return None

        multipolygon_geom = ogr.Geometry(ogr.wkbMultiPolygon)
        for ring in solution:
            ring_geom = ogr.Geometry(ogr.wkbLinearRing)
            for pt in ring:
                ring_geom.AddPoint(pt[0], pt[1])
            polygon_geom = ogr.Geometry(ogr.wkbPolygon)
            polygon_geom.AddGeometry(ring_geom)
            multipolygon_geom.AddGeometry(polygon_geom)
        return multipolygon_geom


    def statistic(self, extent):
        if not self.success:
            print('layer is not opened correctly')
            return

        data = self.spatialQuery(extent)
        if data is None:
            # extent has no intersection with this data, return right now
            return None
        else:
            # clip boundary
            clip_boundary = [[extent[0],extent[2]], [extent[1], extent[2]], [extent[1], extent[3]], [extent[0], extent[3]]]

            grid_val = 0
            # calculate count/length/area/.../ of the features in filtered layer
            for feature in data:
                geom = feature.geometry()
                geometry_type = geom.GetGeometryType()

                if geometry_type == ogr.wkbPoint or geometry_type == ogr.wkbMultiPoint:
                    grid_val = grid_val + 1
                elif geometry_type == ogr.wkbLineString or geometry_type == ogr.wkbMultiLineString:
                    clipped_geom = self.clipPolyline(clip_boundary, geom, geometry_type)
                    if clipped_geom is not None:
                        grid_val = grid_val + clipped_geom.Length()
                elif geometry_type == ogr.wkbPolygon:
                    clipped_geom = self.clipPolygon(clip_boundary, geom, geometry_type)
                    if clipped_geom is not None:
                        grid_val = grid_val + clipped_geom.GetArea()
                elif geometry_type == ogr.wkbMultiPolygon:
                    for polygon in geom:
                        clipped_geom = self.clipPolygon(clip_boundary, polygon, geometry_type)
                        if clipped_geom is not None:
                            grid_val = grid_val + clipped_geom.GetArea()
                else:
                    print 'unknow geometry type: %s' % (geometry_type)
            return grid_val

    