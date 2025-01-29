# -*- coding: utf-8 -*-
__all__ = ['Sketcher', 'SketchHelper']
import adsk.core, adsk.fusion
import math
from numbers import Number
from collections import deque
from .better_types import (Matrix, Point3D)


class Sketcher(object):
  class State(object):
    def __init__(self, transform, as_construction, as_fixed):
      self.__transform = transform
      self.__as_construction = as_construction
      self.__as_fixed = as_fixed

    @property
    def transform(self): return self.__transform

    @property
    def as_construction(self): return self.__as_construction

    @property
    def as_fixed(self): return self.__as_fixed

  def __init__(self, sketch):
    self._sketch = sketch
    self._g = sketch.sketchCurves
    self._state_stack = []
    self._active_transform = Matrix()
    self._path = []
    self._point_buffer = deque()
    self._as_construction = False
    self._as_fixed = False

  def compute_deferred_on(self):
    """Compute deferred is NOT tracked as part of 'state'."""
    self._sketch.isComputeDeferred = True
    return self

  def compute_deferred_off(self):
    """Compute deferred is NOT tracked as part of 'state'."""
    self._sketch.isComputeDeferred = False
    return self

  def construction_on(self):
    """note: setting construction_on has a significant performance hit even with isComputeDeferred!"""
    self._as_construction = True
    return self

  def construction_off(self):
    self._as_construction = False
    return self

  def fixed_on(self):
    self._as_fixed = True
    return self

  def fixed_off(self):
    self._as_fixed = False
    return self

  def _apply_decorations(self, sketch_entity):
    # setting these (mostly/only? construction) is a slow process - dont know why but it is!
    if self._as_construction: sketch_entity.isConstruction = self._as_construction
    if self._as_fixed: sketch_entity.isFixed = self._as_fixed

  def begin_path(self, clear_state=True):
    self._path = []
    self._point_buffer = deque()
    if clear_state: self.clear_state()
    return self

  @property
  def path(self):
    return self._path

  def save(self):
    self._state_stack.append(Sketcher.State(
        self._active_transform.copy(),
        self._as_construction,
        self._as_fixed))
    return self

  def restore(self):
    assert self._state_stack, 'Attempted to restore state but stack was empty!'
    state = self._state_stack.pop()

    self._active_transform = state.transform
    self._as_construction = state.as_construction
    self._as_fixed = state.as_fixed
    return self

  def clear_state(self):
    self._state_stack = []
    self._active_transform = Matrix()
    self._as_construction = False
    self._as_fixed = False

  @property
  def transform(self):
    return self._active_transform.copy()

  @transform.setter
  def transform(self, matrix):
    self._active_transform = Matrix(matrix)

  def identity(self):
    self._active_transform = Matrix()
    return self

  def translate(self, x_or_point, y=0, z=0):
    self._active_transform.translate(x_or_point, y, z)
    return self

  def rotate_z(self, angle, as_degrees=False):
    if as_degrees: angle = math.radians(angle)
    self._active_transform.rotate_z(angle)
    return self;

  def scale(self, x=1, y=1, z=1):
    self._active_transform.scale(x, y, z)
    return self

  def reflect_about_x_axis(self):
    return self.scale(1, -1, 1)

  def reflect_about_y_axis(self):
    return self.scale(-1, 1, 1)

  def push(self, x_or_point, y=0, z=0):
    if isinstance(x_or_point, Number):
      x_or_point = Point3D(x_or_point, y, z)
    self._point_buffer.append(self._active_transform.transform(x_or_point))
    return self

  def push_all(self, points):
    self._point_buffer.extend(self._active_transform.transform(points))
    return self

  def push_close(self):
    if self._path:
      p = self._path[0].startSketchPoint
    else:
      p = self._point_buffer.popleft()
      self._point_buffer.appendleft(p)
    self._point_buffer.append(p)
    return self

  def _pick_from_point(self):
    return self._path[-1].endSketchPoint if self._path else self._point_buffer.popleft()

  def _assert_point_buffer_empty(self):
    assert not self._point_buffer, 'Expected point buffer to be empty, but was not!'

  def draw_line(self):
    p1 = self._pick_from_point()
    p2 = self._point_buffer.popleft()
    e = self._g.sketchLines.addByTwoPoints(p1, p2)
    self._apply_decorations(e)
    self._path.append(e)
    self._assert_point_buffer_empty()
    return e

  def draw_arc(self):
    p1 = self._pick_from_point()
    p2 = self._point_buffer.popleft()
    p3 = self._point_buffer.popleft()
    e = self._g.sketchArcs.addByThreePoints(p1, p2, p3)
    self._apply_decorations(e)
    self._path.append(e)
    self._assert_point_buffer_empty()
    return e

  def draw_spline(self):
    oc = adsk.core.ObjectCollection.create()
    oc.add(self._pick_from_point())
    for item in self._point_buffer:
      oc.add(item)
    e = self._g.sketchFittedSplines.add(oc)
    self._apply_decorations(e)
    self._path.append(e)
    self._point_buffer.clear()
    return e

  def draw_circle_off_path(self, radius, x_or_point=None, y=None, z=0):
    """Radius is NOT scaled by the transformation."""
    if x_or_point is None:
      p = self._pick_from_point()
    elif isinstance(x_or_point, Number):
      p = Point3D(x_or_point, y, z)
    e = self._g.sketchCircles.addByCenterRadius(p, radius)
    self._apply_decorations(e)
    return e


class SketchHelper(object):
  CLOSE_ENOUGH = 0.00001
  def __init__(self, sketch):
    self.sketch = sketch
    self.points = []
    self.curves = []

  def clear(self):
    self.points.clear()
    self.curves.clear()

  def _find_point(self, point, max_distance=CLOSE_ENOUGH):
    for p in self.points:
      if abs(point.distanceTo(p.geometry)) <= max_distance:
        return p
    return None

  def _find_sketch_point(self, sketch_point, max_distance=CLOSE_ENOUGH):
    return self._find_point(sketch_point.geometry, max_distance)

  def track_point(self, point, reuse=True):
    if reuse:
      p = self._find_point(point)
      if not p:
        p = self.sketch.sketchPoints.add(point)
        self.points.append(p)
    else:
      p = self.sketch.sketchPoints.add(point)
    return p

  def merge_or_track_sketch_point(self, sketch_point):
    tracked_point = self._find_sketch_point(sketch_point)
    if not tracked_point:
      self.points.append(sketch_point)
      tracked_point = sketch_point
    else:
      tracked_point.merge(sketch_point)
    return tracked_point

  def add_line(self, from_point, to_point):
    curve = self.sketch.sketchCurves.sketchLines.addByTwoPoints(
      self.track_point(from_point),
      self.track_point(to_point))
    self.curves.append(curve)
    return curve

  def add_arc_by_center_start_sweep(self, center, start, sweep, expect_end=None):
    curve = self.sketch.sketchCurves.sketchArcs.addByCenterStartSweep(center, start, sweep)
    self.merge_or_track_sketch_point(curve.startSketchPoint)
    self.merge_or_track_sketch_point(curve.endSketchPoint)
    self.curves.append(curve)
    if expect_end:
      assert curve.geometry.endPoint.distanceTo(expect_end) <= SketchHelper.CLOSE_ENOUGH or curve.geometry.startPoint.distanceTo(expect_end) <= SketchHelper.CLOSE_ENOUGH, 'End point of arc was not in the expected location. Expected ({}, {}) was ({}, {})'.format(expect_end.x, expect_end.y, curve.geometry.endPoint.x, curve.geometry.endPoint.y)
    return curve

  def add_arc_by_center_start_sweep_degrees(self, center, start, sweep_degrees, expect_end=None):
    return self.add_arc_by_center_start_sweep(center, start, math.radians(sweep_degrees) , expect_end)

