import adsk.core, adsk.fusion, adsk.cam, traceback
from . import fusion360utils as futil
import math

def create_rotate_matrix(norm, angle):
    mat = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    nx = norm.x
    ny = norm.y
    nz = norm.z
    cth = math.cos(angle / 2.0)
    sth = math.sin(angle / 2.0)
    mat[0] = cth + nx**2 * (1-cth)
    mat[1] = nx * ny * (1-cth) - nz * sth
    mat[2] = nx * nz * (1-cth) + ny * sth
    mat[3] = ny * nx * (1-cth) + nz * sth
    mat[4] = cth + ny**2 * (1-cth)
    mat[5] = ny * nz * (1-cth) - nx * sth
    mat[6] = nz * nx * (1-cth) - ny * sth
    mat[7] = nz * ny * (1-cth) + nx * sth
    mat[8] = cth + nz**2 * (1-cth)
    return mat

def calc_multiply(matrix, vector):
    x = matrix[0] * vector.x + matrix[1] * vector.y + matrix[2] * vector.z
    y = matrix[3] * vector.x + matrix[4] * vector.y + matrix[5] * vector.z
    z = matrix[6] * vector.x + matrix[7] * vector.y + matrix[8] * vector.z
    return adsk.core.Vector3D.create(x, y, z)

def get_angle(v1, v2):
    cth = (v1.x * v2.x + v1.y * v2.y + v1.z * v2.z) / math.sqrt(v1.x**2 + v1.y**2 + v1.z**2) / math.sqrt(v2.x**2 + v2.y**2 + v2.z**2)
    if cth > 1.0:
        cth = 1.0
    elif cth < -1.0:
        cth = -1.0
    th = math.acos(cth)
    return th