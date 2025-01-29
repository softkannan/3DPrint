# -*- coding: utf-8 -*-
__all__ = ['GraphicSketch']
import adsk.fusion
from ..drawing.better_types import (format_point, ObjectCollectionToList)


class GraphicSketch(object):
  """Draws with "Custom Graphics" instead of a real sketch."""

  def __init__(self, graphics_group):
    self._g = graphics_group
    self._sketch_curves = _SketchCurves(self)
    self._sketch_points = _SketchPoints(self)
    self._isComputeDeferred = False
    self._areProfilesShown = True

  @property
  def isComputeDeferred(self):
    return self._isComputeDeferred

  @isComputeDeferred.setter
  def isComputeDeferred(self, value):
    self._isComputeDeferred = value

  @property
  def areProfilesShown(self):
    return self._areProfilesShown

  @areProfilesShown.setter
  def areProfilesShown(self, value):
    self._areProfilesShown = value

  @property
  def context(self):
    return adsk.fusion.CustomGraphicsGroup.cast(self._g)

  @property
  def sketchCurves(self):
    return self._sketch_curves

  @property
  def sketchPoints(self):
    return self._sketch_points


def _new_point(point):
  return point.geometry if isinstance(point, adsk.fusion.SketchPoint) else point.copy()


class _SketchCurves(object):
  def __init__(self, graphic_sketch):
    self._graphic_sketch = graphic_sketch
    self._sketch_arcs = _SketchArcs(graphic_sketch)
    self._sketch_fitted_splines = _SketchFittedSplines(graphic_sketch)
    self._sketch_lines = _SketchLines(graphic_sketch)

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
  def __init__(self, graphic_sketch):
    self._graphic_sketch = graphic_sketch

  def add(self, point):
    assert False, 'SketchPoints add not implemented'


class _SketchArcs(object):
  def __init__(self, graphic_sketch):
    self._graphic_sketch = graphic_sketch

  def addByThreePoints(self, startPoint, point, endPoint):
    self._graphic_sketch.context.addCurve(adsk.core.Arc3D.createByThreePoints(startPoint, point, endPoint))
    return _FakeShape(startPoint, endPoint)


class _SketchFittedSplines(object):
  def __init__(self, graphic_sketch):
    self._graphic_sketch = graphic_sketch

  def add(self, point_collection):
    points = ObjectCollectionToList(point_collection)
    raw_coords = []
    for p in points:
      raw_coords.append(p.x)
      raw_coords.append(p.y)
      raw_coords.append(p.z)
    coords = adsk.fusion.CustomGraphicsCoordinates.create(raw_coords)
    self._graphic_sketch.context.addLines(coords, [], True, [])
    return _FakeShape(points[0], points[-1])


class _SketchLines(object):
  def __init__(self, graphic_sketch):
    self._graphic_sketch = graphic_sketch

  def addByTwoPoints(self, startPoint, endPoint):
    raw_coords = [
      startPoint.x, startPoint.y, startPoint.z,
      endPoint.x, endPoint.y, endPoint.z,
    ]
    coords = adsk.fusion.CustomGraphicsCoordinates.create(raw_coords)
    self._graphic_sketch.context.addLines(coords, [], False)
    return _FakeShape(startPoint, endPoint)


#def _resolve_point(point):
#  return point.geometry if isinstance(point, adsk.fusion.SketchPoint) else point.copy()

class _FakeShape(adsk.core.Base):
  def __init__(self, begin, end):
    self.startSketchPoint = _new_point(begin)
    self.startSketchPoint.geometry = self.startSketchPoint
    self.endSketchPoint = _new_point(end)
    self.endSketchPoint.geometry = self.endSketchPoint