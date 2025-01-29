# -*- coding: utf-8 -*-
__all__ = ['PatternBuilder', 'Shape', 'Point', 'Line', 'Arc', 'Pline', 'Spline']
import math
import adsk.core, adsk.fusion
from .better_types import (Point3D, Matrix, format_point, points_eq)
from ..utils.message_box import message_box
from ..utils.timers import RelayStopwatch

# BEHAVIORS
# while building we reduce points (defining each shape) which overlap
# if a line ends up with one point we reject it silently
# if an arc ends up with 2 points we ERR
# if an arc ends up with one point we reject it silently
# if a spline/pline ends up with 1 point we reject it silently
# plines are mearly a construct - each leg of a pline is drawn as a line
#
# A pattern may be closed by having co-located start and end points
# All shapes which are part of a pattern must form an unbroken chain
#
# Rev 1 Limitations
#   shapes must be built in chain order - start/end points may be transposed between links
#

# TODO: optmize pattern (combine lines, arcs)
# TODO: allow adding shapes in any order
# TODO: rename PatternBuilder to pattern, change make_pattern to optimize(), change add method names to be add_foo
class PatternBuilder(object):
  def __init__(self):
    self.clear()

  def clear(self):
    self._shapes = []

  def _reduce(self, points):
    p = points[0]
    po = [p.copy()]
    for i in range(1, len(points)):
      p2 = points[i]
      if not points_eq(p, p2):
        po.append(p2.copy())
        p = p2
    return po

  @property
  def first_point(self):
    return self.points[0]

  @property
  def last_point(self):
    return self.points[-1]
    
  def arc(self, p1, p2, p3):
    points = self._reduce([p1, p2, p3])
    lp = len(points)
    if lp == 3:
      self._shapes.append(Arc(points))
    elif lp == 2:
      raise ValueError('arc requires 3 distinct points')
    return self
    
  def circle(self, center, radius):
    m = Matrix()
    m.translate(center)
#    points = m.transform([Point3D(radius, 0), Point3D(-radius, 0), Point3D(radius, 0)])
#    self._shapes.append(Arc(points))
    points = m.transform([Point3D(radius, 0), Point3D(0, radius), Point3D(-radius, 0), Point3D(0, -radius)])
    self.arc(points[0],points[1],points[2])
    self.arc(points[2],points[3],points[0])

  def line(self, p1, p2):
    points = self._reduce([p1, p2])
    if len(points) == 2:
      self._shapes.append(Line(points))
    return self

  def pline(self, points):
    points = self._reduce(points)
    if len(points) > 1:
      self._shapes.append(Pline(points))
    return self

  def spline(self, points):
    points = self._reduce(points)
    if len(points) > 1:
      self._shapes.append(Spline(points))
    return self

  def pattern(self, pattern):
    self._shapes.append(pattern)

  def __str__(self):
    z = ''
    for s in self._shapes:
      z += str(s)
    return z

  def _pick_start_point(self):
    s0_fp = self._shapes[0].first_point
    s0_lp = self._shapes[0].last_point
    s1_fp = self._shapes[1].first_point
    s1_lp = self._shapes[1].last_point
    if points_eq(s0_lp, s1_fp): return s0_fp
    if points_eq(s0_fp, s1_fp): return s0_lp
    if points_eq(s0_lp, s1_lp): return s0_fp
    if points_eq(s0_fp, s1_lp): return s0_lp
    raise ValueError('First and second shape do not share an endpoint - failed to identify a starting point.\n' + str(self))

  def debug_draw(self, sketch, transform=None):
    shapes = []
    for shape in self._shapes:
      shapes.extend(shape.draw(sketch, transform))
    return shapes

  def make_pattern(self):
    if not self._shapes:
      raise ValueError('Cannot create an empty pattern.')

    if len(self._shapes) == 1:
      start_at = self._shapes[0].first_point
    else:
      start_at = self._pick_start_point()

    # message_box('starting at: ' + format_point(start_at))
    pat = _Pattern(start_at)
    for shape in self._shapes:
      pat._append(shape)

    self._shapes = [pat]
    return pat

  def circular_pattern(self, count, center=None):
    if not self._shapes:
      raise ValueError('Cannot create an empty pattern.')
    if len(self._shapes) > 1 or not isinstance(self._shapes[0], _Pattern):
      self.make_pattern()

    pat = self._shapes[0]
    rot = 2 * math.pi / count
    for i in range(1, count):
      m = Matrix()
      if center: m.translate(center)
      m.rotate_about_z_axis(rot * i)
      if center: m.translate(-center.x, -center.y, -center.z)
      m.purify()
      self._shapes.append(pat.transform_copy(m))
    st = ''
    for s in self._shapes:
      st += str(s)
      st += '\n\n'
    # message_box(st)

    return self.make_pattern()


class Shape(object):
  def __init__(self, points):
    assert points is not None
    self.points = points

  @property
  def first_point(self):
    return self.points[0]

  @property
  def last_point(self):
    return self.points[-1]

  @property
  def name(self):
    return type(self).__name__

  def __str__(self):
    s = '{}: [\n  '.format(self.name)
    s += '\n  '.join([format_point(p) for p in self.points])
    s += '\n]\n'
    return s

  def draw(self, sketch, transform=None):
    raise NotImplemented('Drawing is not implemented on shape: ' + self.name)

  def _transformed_points(self, transform):
    if transform:
      return transform.transform(self.points)
    else:
      return self.points.copy()


class _Pattern(Shape):
  def __init__(self, start_at):
    super().__init__([start_at])
    self._ops = [Point(start_at).make_op()]
    self.last_draw_timer = None

  def transform_copy(self, matrix=None):
    if not matrix:
      matrix = Matrix()
    p = _Pattern(Point3D(0,0))
    p.points = matrix.transform(self.points)
    p._ops = self._ops.copy()
    return p

  @property
  def is_closed(self):
    return points_eq(self.last_point, self.first_point)
    
  def close(self):
    if not self.is_closed:
      self._append(Line([self.first_point, self.last_point]))

  def _append(self, shape):
    op = shape.make_op()
    if points_eq(self.last_point, shape.first_point):
      points = shape.points[1:]
    elif points_eq(self.last_point, shape.last_point):
      points = shape.points[-2::-1]
      if isinstance(op, list):
        op.reverse()
    else:
      raise ValueError('Cannot extend pattern with the given shape ({}) - '
          'shape does not connect to current pattern endpoint.\n\n'
          'Pattern Thusfar:\n{}'
          'Attempted Shape:\n{}\n\n'.format(shape.name, str(self), str(shape)))

    self.points.extend(points)
    if not isinstance(op, list):
      self._ops.append(op)
    else:
      self._ops.extend(op)
    # shape.points = None  # this would (might?) save memory but prevents shape re-use - maybe that's good maybe bad - TBD

  def optimize(self):
    """Combines operations where reasonable to do so. E.g. arcs which are connected and share a center point."""
    points = self.points

    i = 1
    opi = 1
    ops_len = len(self._ops)
    new_ops = [self._ops[0]]
    new_points = [points[0]]
    last_op = self._ops[0]

    while opi < ops_len:
      keep = True
      op = self._ops[opi]
      if op.name == last_op.name:
        if op.name == 'arc':
          if points_eq(Arc.center(points, i, points[i-1]), Arc.center(points, i-2, points[i-3])):
            new_points[-2] = points[i-1]
            new_points[-1] = points[i+1]
            keep = False
        elif op.name == 'line':
          # TODO: optimize lines
          pass

      if keep:
        for j in range(op.step):
          new_points.append(points[i])
          i += 1
        new_ops.append(op)
      else:
        i += op.step
      opi += 1
      last_op = op

    # optimize when the first and last operation can be joined (closed shapes only). E.g.: [arc ... arc]
    if self.is_closed and ops_len > 2:
      op = self._ops[1]
      if op.name == last_op.name:
        if op.name == 'arc':
          if points_eq(Arc.center(points, 1, points[0]), Arc.center(points, i-2, points[i-3])):
            new_points[1] = new_points[0]
            new_points[0] = new_points[-3]
            keep = False
        elif op.name == 'line':
          # TODO: optimize lines
          pass
      if not keep:
        pops = new_ops.pop().step
        for j in range(pops):
          new_points.pop()

    self.points = new_points
    self._ops = new_ops
    return self

  def draw(self, sketch, transform=None):
    timer = RelayStopwatch()
    timer.start_section('deferring sketch computation')
    was_compute_deferred = sketch.isComputeDeferred
    was_profiles_shown = sketch.areProfilesShown
    if not was_compute_deferred:
      sketch.isComputeDeferred = True
    if was_profiles_shown:
      sketch.areProfilesShown = False
    timer.start_section('transform points')
    points = self._transformed_points(transform)

    # setup the start point
    last_end = points[0]
    i = 1
    step = 1
    opi = 1
    ops_len = len(self._ops)
    shapes = []

    # draw the first shape out of the loop to deal with closed shapes and not get a seam point
    timer.start_section('draw ' + self._ops[opi].name)
    (e, last_end, step) = self._ops[opi](points, i, sketch, last_end)
    shapes.append(e)
    i += step
    opi += 1
    if self.is_closed:
      # arcs cause a problem - address it
      points[-1] = e.startSketchPoint if points_eq(points[-1], e.startSketchPoint.geometry) else e.endSketchPoint

    # draw the rest
    while opi < ops_len:
      timer.start_section('draw ' + self._ops[opi].name)
      (e, last_end, step) = self._ops[opi](points, i, sketch, last_end)
      shapes.append(e)
      i += step
      #last_end = points[i-1]  # stop passing sketchpoints forward
      opi += 1

    timer.start_section('restoring sketch computation settings')
    if was_compute_deferred != sketch.isComputeDeferred:
      sketch.isComputeDeferred = was_compute_deferred
    if was_profiles_shown != sketch.areProfilesShown:
      sketch.areProfilesShown = was_profiles_shown
    timer.stop()
    self.last_draw_timer = timer
    assert i == len(points), 'Woops, the pattern didnt draw all points!'
    return shapes

  def draw_graphic(self, graphics_group, transform_matrix=None):
    if not transform_matrix:
      transform_matrix = Matrix()
    gg = adsk.fusion.CustomGraphicsGroup.cast(graphics_group)
    raw_coords = []
    for p in transform_matrix.transform(self.points):
      raw_coords.append(p.x)
      raw_coords.append(p.y)
      raw_coords.append(p.z)
    coords = adsk.fusion.CustomGraphicsCoordinates.create(raw_coords)
    gg.addLines(coords, [], True, [])

  def make_op(self):
    return self._ops[1:]  # drop the start point op

  def __str__(self):
#    s = 'Pattern points: [\n  '
#    s += '\n  '.join([format_point(p) for p in self.points])
#    s += '\n]\n'
#    s += 'Pattern ops: [\n  '
#    s += '\n  '.join([op.name for op in self._ops])
#    s += '\n]\n'
    i = 0
    s = 'Pattern: ['
    for op in self._ops:
      for j in range(op.step):
        if i > 0: s += op.name  # end the previous line
        s += '\n{0: >6} '.format(op.name)
        s += format_point(self.points[i],'{: >11.6f}') + ' '
        i += 1
    s += 'COSED' if self.is_closed else 'OPEN'
    s += '\n]\n'
    return s


class Point(Shape):
  def __init__(self, point):
    super().__init__([point])

  def make_op(self):
    def op(points, from_index, sketch, from_point):
      e = sketch.sketchPoints.add(points[from_index])
      #return (e, points[from_index], 1)
      return (e, e, 1)
    op.name = 'point'
    op.step = 1
    return op

  def draw(self, sketch, transform=None):
    p = self._transformed_points(transform)[0]
    return [sketch.sketchPoints.add(p)]


class Arc(Shape):
  def __init__(self, points):
    super().__init__(points)

  def make_op(self):
    def op(points, from_index, sketch, from_point):
      c = points[from_index]
      if isinstance(c, adsk.fusion.SketchPoint):
        c = c.geometry
      e = sketch.sketchCurves.sketchArcs.addByThreePoints(from_point, c, points[from_index + 1])
      # arcs dont respect the given draw order - they are always drawn in CCW order apparently
      ep = e.endSketchPoint if points_eq(points[from_index + 1], e.endSketchPoint.geometry) else e.startSketchPoint
      return (e, ep, 2)
      #return (e, points[from_index + 1], 2)
    op.name = 'arc'
    op.step = 2
    return op

  @staticmethod
  def center(points, from_index, from_point):
    # https://math.stackexchange.com/users/122782/g-kov
    a = points[from_index]
    b = points[from_index]
    c = points[from_index]
    assert a.z == b.z and b.z == c.z, "For now, Arcs must lay on the XY plane to compute thier center point."

    ox = (a.x**2 - b.x**2) + (a.y**2 - b.y**2)
    oy = (b.x**2 - c.x**2) + (b.y**2 - c.y**2)
    return Point3D(ox, oy, a.z)

  def draw(self, sketch, transform=None):
    points = self._transformed_points(transform)
    c = points[1]
    if isinstance(c, adsk.fusion.SketchPoint):
      c = c.geometry
    return [sketch.sketchCurves.sketchArcs.addByThreePoints(points[0], c, points[2])]


class Line(Shape):
  def __init__(self, points):
    super().__init__(points)

  def make_op(self):
    def op(points, from_index, sketch, from_point):
      e = sketch.sketchCurves.sketchLines.addByTwoPoints(from_point, points[from_index])
      return (e, e.endSketchPoint, 1)
      #return (e, points[from_index], 1)
    op.name = 'line'
    op.step = 1
    return op

  def draw(self, sketch, transform=None):
    points = self._transformed_points(transform)
    return [sketch.sketchCurves.sketchLines.addByTwoPoints(points[0], points[1])]


class Pline(Shape):
  def __init__(self, points):
    super().__init__(points)

  def make_op(self):
    def op(points, from_index, sketch, from_point):
      e = sketch.sketchCurves.sketchLines.addByTwoPoints(from_point, points[from_index])
      return (e, e.endSketchPoint, 1)
      #return (e, points[from_index], 1)
    op.name = 'line'
    op.step = 1
    return [op]*(len(self.points) - 1)

  def draw(self, sketch, transform=None):
    points = self._transformed_points(transform)
    shapes = []
    for i in range(1, len(points)):
      shapes.append(sketch.sketchCurves.sketchLines.addByTwoPoints(points[i-1], points[i]))
    return shapes


class Spline(Shape):
  def __init__(self, points):
    super().__init__(points)

  def make_op(self):
    op_nodes = len(self.points) - 1
    def op(points, from_index, sketch, from_point):
      oc = adsk.core.ObjectCollection.create()
      oc.add(from_point)
      for i in range(from_index, from_index + op_nodes):
        oc.add(points[i])

      e = sketch.sketchCurves.sketchFittedSplines.add(oc)
      return (e, e.endSketchPoint, op_nodes)
      #return (e, points[from_index+op_nodes-1], 1)
    op.name = 'spline'
    op.step = op_nodes
    return op

  def draw(self, sketch, transform=None):
    points = self._transformed_points(transform)
    oc = adsk.core.ObjectCollection.create()
    for p in points:
      oc.add(p)
    return [sketch.sketchCurves.sketchFittedSplines.add(oc)]
