import math
from random import randint

import EllipticCurve as ec
import UtilityNum as num



class ECDHKE:
    def __init__(self, a, b, p, g):
        self.E = ec.EllipticCurve(a, b, p)
        if not self.E.is_element(g):
            raise Exception("Error: given generator must be on the curve")
        self.g = g
        hasses_bound = int(p - (2 * math.sqrt(p)))
        self.x = randint(hasses_bound // 2, hasses_bound)
        self.X = self.E.multiply(self.x, self.g)

    def get_shared_secret(self, Y):
        return self.E.multiply(self.x, Y)
