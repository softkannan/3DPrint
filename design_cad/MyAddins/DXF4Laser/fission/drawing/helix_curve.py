# -*- coding: utf-8 -*-
__all__ = ['HelixCurve', 'LinearInterpolation', 'CosineInterpolation', 'PolynomicInterpolation']
from collections import namedtuple
from .better_types import (Point3D, CylindricalCoord, ObjectCollectionFromList)
from ..utils.message_box import message_box
import math

class HelixCurve(object):
  def __init__(self, radius, helix_angle, rotation=0, z_shift=0):
    self.__radius = radius
    self.__helix_angle = helix_angle
    self.__rotation = rotation
    self.__z_shift = z_shift
    self._calc_rotation_componants()
    self.__is_valid = (
      self.__helix_angle <= math.radians(-0.0001) or
      self.__helix_angle >= math.radians(0.0001))

    self.__c = math.tan(self.__helix_angle) * self.__radius if self.__is_valid else None

  def _calc_rotation_componants(self):
    self.__z_shift_rot = self.__z_shift / (math.tan(self.__helix_angle) * self.__radius)
    self.__cos_rotation = math.cos(self.__rotation + self.__z_shift_rot)
    self.__sin_rotation = math.sin(self.__rotation + self.__z_shift_rot)

  @property
  def rotation(self):
    return self.__rotation

  @rotation.setter
  def rotation(self, value):
    self.__rotation = value
    self._calc_rotation_componants()

  @property
  def z_shift(self):
    return self.__z_shift

  @z_shift.setter
  def z_shift(self, value):
    self.__z_shift = value
    self._calc_rotation_componants()

  @property
  def total_rotation(self):
    return self.__rotation + self.__z_shift_rot

  @property
  def is_valid(self):
    return self.__is_valid

  @property
  def vertical_loop_seperation(self):
    return self.__c * 2 * math.pi if self.__is_valid else None

  @property
  def helix_angle(self):
    return self.__helix_angle if self.__is_valid else None

  @property
  def radius(self):
    return self.__radius if self.__is_valid else None

  @property
  def curvature(self):
    r = self.__radius
    c = self.__c
    return r / (r*r + c*c) if self.__is_valid else None

  @property
  def torsion(self):
    r = self.__radius
    c = self.__c
    return c / (r*r + c*c) if self.__is_valid else None

  def t_for(self, displacement):
    return displacement / self.__c if self.__is_valid else None

  def angle_at_displacement(self, displacement):
    """Angle between 0 and 2PI."""
    t = self.t_for(displacement)
    a = t + self.rotation
    a %= 2 * math.pi
    return a

  def locus(self, t):
    r = self.__radius
    c = self.__c
    return math.sqrt(r*r + c*c) * t if self.__is_valid else None

  def get_point(self, t):
    """Gets a 3D point along the Helical path.

    Args:
      self - self
      t - number - one revolution of the helix spans t from 0 to 2PI.
    Returns:
      adsk.core.Point3D
    """
    x = self.__radius * math.cos(t)
    y = self.__radius * math.sin(t)
    z = self.__c * t
    if self.total_rotation != 0:
      xr = x * self.__cos_rotation - y * self.__sin_rotation
      y = x * self.__sin_rotation + y * self.__cos_rotation
      x = xr
    return Point3D(x, y, z + self.__z_shift)

  def get_points(self, from_t, to_t, steps=None, bookends=0):
    points = []
    t_range = to_t - from_t
    if not steps:
      steps = int(18 * t_range / math.pi * 2)
    if steps < 0:
      steps *= -1
    if steps < 5:
      steps = 5
    step = 1.0 / (steps - 1)

    for i in range(-bookends, steps + bookends):
      t = from_t + t_range * step * i
      points.append(self.get_point(t))
    return points

  def offset(self, distance):
    return self.project(self.radius + distance)

  def project(self, new_radius):
    r2 = new_radius
    assert r2 != 0
    theta = math.atan(self.__c / abs(r2))
    if r2 < 0:
      theta = -theta
    return HelixCurve(abs(r2), theta, self.__rotation, self.__z_shift)


class InterpolationBase(object):
  @property
  def min_nodes(self):
    return 3

  def __call__(self, a, b, p):
    """Computes a value given the inital and final values a and b respectively and a value of p between 0 and 1.

    Args
      a: inital value
      b: final value
      p: progression of transform ranging from 0 to 1 inclusive.
    """
    pass

class LinearInterpolation(InterpolationBase):
  def __call__(self, a, b, p):
    if p == 1.0:
      return b
    return a + (b - a) * p

class CosineInterpolation(InterpolationBase):
  def __init__(self, ease='both'):
    if ease == 'both':
      self._f = self._ease_both
    elif ease == 'in':
      self._f = self._ease_in
    elif ease == 'out':
      self._f = self._ease_out

  def _ease_out(self, a, b, p):
    return a + (b - a) * (1 - math.cos((math.pi / 2) * p))

  def _ease_in(self, a, b, p):
    return b - (b - a) * (math.cos((math.pi / 2) + (math.pi / 2) * p) + 1)

  def _ease_both(self, a, b, p):
    return a + (b - a) * ((math.cos(math.pi * p) - 1) / -2)

  def __call__(self, a, b, p):
    if p == 0.0:
      return a
    if p == 1.0:
      return b
    if a == b:
      return a
    return self._f(a, b, p)


class PolynomicInterpolation(InterpolationBase):
  # ease out, ease in, ease both
  def __init__(self, exponent, ease='both'):
    self._exp = exponent
    if ease == 'both':
      self._f = self._ease_both
    elif ease == 'in':
      self._f = self._ease_in
    elif ease == 'out':
      self._f = self._ease_out

  @property
  def min_nodes(self):
    x = abs(self._exp)
    if x > 1:
      return int(x * 2) + 1
    elif self._exp == 0:
      return 3
    else:
      return int(2 / x) + 1

  def _ease_out(self, a, b, p):
    if p <= 0.0:
      return a
    if p >= 1.0:
      return b
    return a + (b - a) * p**self._exp

  def _ease_in(self, a, b, p):
    if p <= 0.0:
      return a
    if p >= 1.0:
      return b
    return b - (b - a) * (1-p)**self._exp

  def _ease_both(self, a, b, p):
    m = (a + b) / 2
    if p < 0.5:
      return self._ease_out(a, m, 2.0 * p)
    elif p > 0.5:
      return self._ease_in(m, b, 2.0 * (p - 0.5))
    else:
      return m

  def __call__(self, a, b, p):
    return self._f(a,b,p)

class CompundHelicalSegment(object):
  def __init__(self, starting_rotation, ref_radius, spec1, spec2, angular_interpolation, radial_interpolation):
    self._starting_rotation = starting_rotation
    self._ref_radius = ref_radius
    self._spec1 = spec1
    self._spec2 = spec2
    self._angular_interpolation = angular_interpolation
    self._radial_interpolation = radial_interpolation
    self._calc_steps()
    self._calc()
    
  @property
  def cylindrical_cords(self):
    return self._cords

  @property
  def starting_rotation(self):
    return self._starting_rotation

  @property
  def ending_rotation(self):
    return self._cords[-1].a

  @property
  def is_constant_helix_angle(self):
    return self._spec1.a == self._spec2.a

  @property
  def is_constant_radius(self):
    return self._spec1.r == self._spec2.r

  @property
  def twist(self):
    return self.ending_rotation - self.starting_rotation

  @property
  def length(self):
    return self._spec2.z - self._spec1.z

  @property
  def start_z(self):
    return self._spec1.z

  @property
  def end_z(self):
    return self._spec2.z

  def _calc_steps(self):
    dominant_spec = self._spec1 if abs(self._spec1.a) > abs(self._spec2.a) else self._spec2
    c = math.tan(math.pi / 2 - dominant_spec.a) * self._ref_radius
    dz = self._spec2.z - self._spec1.z
    dt = dz / c
    steps = int(9 * dt / math.pi * 2)
    if steps < 0:
      steps *= -1
    if steps < 5:
      steps = 5
    if steps < self._angular_interpolation.min_nodes:
      steps = self._angular_interpolation.min_nodes
    if steps < self._radial_interpolation.min_nodes:
      steps = self._radial_interpolation.min_nodes
    # use an odd number of steps to ensure we always have a "midpoint"
    if steps % 2 == 0:
      steps += 1

    step = 1.0 / (steps - 1)
    self._steps = [i * step for i in range(steps)]
    self._steps[-1] = 1.0

  def _calc(self):
    ret = []
    ia = self._starting_rotation
    r_interp = self._radial_interpolation
    a_interp = self._angular_interpolation
    z_interp = LinearInterpolation()
    s1 = self._spec1
    s2 = self._spec2
    dz = self._steps[1] * (s2.z - s1.z)
    first = True
    last_helix_angle = s1.a
    HALF_PI = math.pi / 2
    #s = ''
    for p in self._steps:
      if first:
        ret.append(CylindricalCoord(s1.r, ia, s1.z))
        first = False
        continue
      r = r_interp(s1.r, s2.r, p)
      helix_angle = a_interp(s1.a, s2.a, p)
      z = z_interp(s1.z, s2.z, p)
      #s += '  r: {:.4}; a: {:.4}; z: {:.4} => '.format(r,math.degrees(a),z)

      a1 = dz / (math.tan(HALF_PI - helix_angle) * self._ref_radius)
      a2 = dz / (math.tan(HALF_PI - last_helix_angle) * self._ref_radius)
      a = (a1 + a2) / 2

      last_helix_angle = helix_angle
      #s += '{:.4} + ia => {:.4}\n'.format(math.degrees(a), math.degrees(a + ia))
      ia += a
      ret.append(CylindricalCoord(r, ia, z))
    self._cords = ret
    #message_box('Initial Rot: {:.4}\nFrom: {}\nTo  : {}\n{}'.format(math.degrees(self._starting_rotation), s1, s2, s))

  def as_points(self):
    return [c.as_point3d() for c in self._cords]
    
  def contains(self, z):
    return self._spec2.z >= z and self._spec1.z <= z
    
  def calc_at(self, z):
    if not self.contains(z):
      return None
    
    ia = self._starting_rotation
    s1 = self._spec1
    s2 = self._spec2
    
    if z == s1.z:
      return CylindricalCoord(s1.r, ia, s1.z)
      
    HALF_PI = math.pi / 2
    dz = z - s1.z
    p = dz / (s2.z - s1.z)
    
    r = self._radial_interpolation(s1.r, s2.r, p)
    helix_angle = self._angular_interpolation(s1.a, s2.a, p)
    a1 = dz / (math.tan(HALF_PI - helix_angle) * self._ref_radius)
    a2 = dz / (math.tan(HALF_PI - s1.a) * self._ref_radius)
    a = (a1 + a2) / 2
    ia += a
    return CylindricalCoord(r, ia, z)    


class CompundHelicalPathBuilder(object):
  def __init__(self, ref_radius):
    self._ref_radius = ref_radius
    self._previous_spec = None
    self._current_rotation = 0
    self._sequence = []
    self._angular_transition = LinearInterpolation()
    self._radial_transition = PolynomicInterpolation(2, 'both')
    self._dirty = True
    self._c_points = None  # array of arrays of clyndrical points, each sub-array corresponds to a segment
    self._e_points = None  # array of arrays of euclidean points, each sub-array corresponds to a segment

  @property
  def c_points(self):
    return self.build()._c_points
    
  @property
  def e_points(self):
    return self.build()._e_points

  @property
  def angular_transition(self):
    return self._angular_transition

  @angular_transition.setter
  def angular_transition(self, value):
    self._angular_transition = value

  @property
  def radial_transition(self):
    return self._radial_transition

  @radial_transition.setter
  def radial_transition(self, value):
    self._radial_transition = value

  def build(self):
    if self._dirty:
      self._c_points = [s.cylindrical_cords for s in self._sequence]
      self._e_points = [s.as_points() for s in self._sequence]
      self._dirty = False
    return self

  def draw(self, sketch):
    splines = sketch.sketchCurves.sketchFittedSplines
    return [splines.add(ObjectCollectionFromList(points)) for points in self.e_points]
    
  def calc_at(self, z):
    for s in self._sequence:
      if s.contains(z):
        return s.calc_at(z)
    return None

  def polynomic_ease(self, exponant=2, ease='both'):
    self._radial_transition = PolynomicInterpolation(2, ease)

  def parabolic_ease_in(self):
    self._radial_transition = PolynomicInterpolation(2, 'in')

  def parabolic_ease_out(self):
    self._radial_transition = PolynomicInterpolation(2, 'out')

  def parabolic_ease_in_and_out(self):
    self._radial_transition = PolynomicInterpolation(2, 'both')

  def linear_ease(self):
    self._radial_transition = LinearInterpolation()

  def cosine_ease(self, ease='both'):
    self._radial_transition = CosineInterpolation(ease)

  def cosine_in(self):
    self._radial_transition = CosineInterpolation('in')

  def cosine_out(self):
    self._radial_transition = CosineInterpolation('out')

  def cosine_in_and_out(self):
    self._radial_transition = CosineInterpolation('both')

  @property
  def segments(self):
    return self._sequence

  @property
  def ref_radius(self):
    return self._ref_radius

  def append(self, z, helix_angle=None, radius=None):
    """Appends a segment.

    Args
      z: z componant of 3D point
      helix_angle: objective helix angle
      radius: objective radius
    """
    assert helix_angle is not None or self._previous_spec is not None, 'helix_angle must be provided at least once.'
    assert radius is not None or self._previous_spec is not None, 'radius must be provided at least once.'
    self._dirty = True
    # assert transition_direction in (-1, 0, 1), 'Invalid transition_direction'
    if radius is None:
      radius = self._previous_spec.r
    if helix_angle is None:
      helix_angle = self._previous_spec.a
    spec = CylindricalCoord(radius, helix_angle, z)

    if self._previous_spec:
      # starting_rotation, ref_radius, spec1, spec2, angular_interpolation, radial_interpolation):
      segment = CompundHelicalSegment(
        self._current_rotation,
        self._ref_radius,
        self._previous_spec,
        spec,
        self._angular_transition,
        self._radial_transition
        )
      # Avoid generating a zero length segment
      if self._previous_spec.r != spec.r or self._previous_spec.z != spec.z:
        self._sequence.append(segment)
      self._current_rotation = segment.ending_rotation

      # assert self._previous_spec.z <= spec.z, 'Out of order?'
    self._previous_spec = spec
    return self
