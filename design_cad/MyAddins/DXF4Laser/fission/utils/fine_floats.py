# -*- coding: utf-8 -*-
import math,  struct

def next_up(x):
  # NaNs and positive infinity map to themselves.
  if math.isnan(x) or (math.isinf(x) and x > 0):
      return x

  # 0.0 and -0.0 both map to the smallest +ve float.
  if x == 0.0:
      x = 0.0

  n = struct.unpack('<q', struct.pack('<d', x))[0]
  if n >= 0:
      n += 1
  else:
      n -= 1
  return struct.unpack('<d', struct.pack('<q', n))[0]

def next_down(x):
  return -next_up(-x)

def next_after(x, y):
  # If either argument is a NaN, return that argument.
  # This matches the implementation in decimal.Decimal
  if math.isnan(x):
      return x
  if math.isnan(y):
      return y

  if y == x:
      return y
  elif y > x:
      return next_up(x)
  else:
      return next_down(x)