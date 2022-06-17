from math import sqrt
from numpy import arccos, rad2deg
import pymap3d as pm


class Point:
    __slots__ = ('x', 'y', 'z')

    # ----------------------------------------------------------------------------------------------
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x: float = float(x)
        self.y: float = float(y)
        self.z: float = float(z)

    # ----------------------------------------------------------------------------------------------
    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x,
                     self.y + other.y,
                     self.z + other.z)

    # ----------------------------------------------------------------------------------------------
    def __iadd__(self, other: "Point") -> "Point":
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    # ----------------------------------------------------------------------------------------------
    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x,
                     self.y - other.y,
                     self.z - other.z)

    # ----------------------------------------------------------------------------------------------
    def __isub__(self, other: "Point") -> "Point":
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    # ----------------------------------------------------------------------------------------------
    def __truediv__(self, other: float) -> "Point":
        return Point(self.x / other,
                     self.y / other,
                     self.z / other)

    # ----------------------------------------------------------------------------------------------
    def __itruediv__(self, other: float) -> "Point":
        self.x /= other
        self.y /= other
        self.z /= other
        return self

    # ----------------------------------------------------------------------------------------------
    def __mul__(self, other: float) -> "Point":
        return Point(self.x * other,
                     self.y * other,
                     self.z * other)

    # ----------------------------------------------------------------------------------------------
    def __imul__(self, other: float) -> "Point":
        self.x *= other
        self.y *= other
        self.z *= other
        return self

    # ----------------------------------------------------------------------------------------------
    def __str__(self):
        return f"Point[x: {self.x}, y: {self.y}, z: {self.z}]"

    # ----------------------------------------------------------------------------------------------
    def __repr__(self):
        return str(self)

    # ----------------------------------------------------------------------------------------------
    def dot(self, other: "Point") -> float:
        return self.x * other.x + self.y * other.y+self.z * other.z

    # ----------------------------------------------------------------------------------------------
    def cross(self, other: "Point") -> "Point":
        return Point(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    # ----------------------------------------------------------------------------------------------
    @property
    def norm(self) -> float:
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    # ----------------------------------------------------------------------------------------------
    @property
    def vector(self) -> list:
        return [self.x, self.y, self.z]


    # ----------------------------------------------------------------------------------------------
    @property
    def angles(self) -> "Point":
        tmp = self / self.norm
        return Point(arccos(tmp.x), arccos(tmp.y), arccos(tmp.z))

    # ----------------------------------------------------------------------------------------------
    @property
    def anglesd(self) -> "Point":
        tmp = self.angles
        return Point(rad2deg(tmp.x), rad2deg(tmp.y), rad2deg(tmp.z))
