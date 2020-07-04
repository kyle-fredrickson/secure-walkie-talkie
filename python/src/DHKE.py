from random import randint

import UtilityNum as num

class DHKE:
    def __init__(self, p, g):
        self.g = g
        self.p = p
        self.x = randint(p // 2, p)
        self.X = pow(self.g, self.x, self.p)

    def get_shared_secret(self, Y):
        return pow(Y, self.x, self.p)
