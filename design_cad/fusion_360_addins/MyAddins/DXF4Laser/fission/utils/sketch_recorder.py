# -*- coding: utf-8 -*-
__all__ = ['SketchRecorder']
import adsk.fusion
from ..drawing.better_types import (format_point, ObjectCollectionToList)

class SketchRecorder(object):
  def __init__(self):
    self._commands = []
    self._sketch_curves = _SketchCurves(self)
    self._sketch_points = _SketchPoints(self)
    pass

  def log(self, cmd):
    self._commands.append(cmd)

  def __str__(self):
    return '\n'.join(self._commands)

  @property
  def sketchCurves(self):
    return self._sketch_curves

  @property
  def sketchPoints(self):
    return self._sketch_points


def _new_point(point):
  if isinstance(point, adsk.fusion.SketchPoint): point = point.geometry
  return 'Point3D' + format_point(point)


class _SketchCurves(object):
  def __init__(self, recorder):
    self._recorder = recorder
    self._sketch_arcs = _SketchArcs(recorder)
    self._sketch_fitted_splines = _SketchFittedSplines(recorder)
    self._sketch_lines = _SketchLines(recorder)

  @property
  def sketchArcs(self):
    return self._sketch_arcs

  @property
  def sketchFittedSplines(self):
    return self._sketch_fitted_splines

  @property
  def sketchLines(self):
    return self._sketch_lines



class _SketchPoints(object):
  def __init__(self, recorder):
    self._recorder = recorder
  def add(self, point):
    cmd = 'sketch.sketchPoints.add(' + _new_point(point) + ')'
    self._recorder.log(cmd)


class _SketchArcs(object):
  def __init__(self, recorder):
    self._recorder = recorder
  def addByThreePoints(self, startPoint, point, endPoint):
    cmd = 'sketch.sketchCurves.sketchArcs.addByThreePoints(' + _new_point(startPoint) + ', ' + _new_point(point) + ', ' + _new_point(endPoint) + ')'
    self._recorder.log(cmd)
    return _FakeShape(startPoint, endPoint)


class _SketchFittedSplines(object):
  def __init__(self, recorder):
    self._recorder = recorder
  def add(self, point_collection):
    points = ObjectCollectionToList(point_collection)
    self._recorder.log('oc = ObjectCollection()')
    for p in points:
      self._recorder.log('oc.add(' + _new_point(p) + ')')
    self._recorder.log('sketch.sketchCurves.sketchFittedSplines.add(oc)')
    return _FakeShape(points[0], points[-1])


class _SketchLines(object):
  def __init__(self, recorder):
    self._recorder = recorder
  def addByTwoPoints(self, startPoint, endPoint):
    cmd = 'sketch.sketchCurves.sketchLines.addByTwoPoints(' + _new_point(startPoint) + ', ' + _new_point(endPoint) + ')'
    self._recorder.log(cmd)
    return _FakeShape(startPoint, endPoint)


def _resolve_point(point):
  return point.geometry if isinstance(point, adsk.fusion.SketchPoint) else point.copy()

class _FakeShape(adsk.core.Base):
  def __init__(self, begin, end):
    self.startSketchPoint = _resolve_point(begin)
    self.startSketchPoint.geometry = self.startSketchPoint
    self.endSketchPoint = _resolve_point(end)
    self.endSketchPoint.geometry = self.endSketchPoint