import UtilityNum as num

class EllipticCurve:
    IDENTITY = "O"

    """
    Creates an instance of an elliptic curve over the field Z_p with points satisfying
    y^2 = x^3 + ax + b
    """
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p

    """
    Computes point addition between p1 and p2 over the group

    _add : pt1 (x,y), pt2 (x,y) -> pt3 (x,y)
    """
    def _add(self, p1, p2):
        if not (self.is_element(p1) and self.is_element(p2)):
            raise Exception("input to _add was not an element of the group")

        if EllipticCurve.IDENTITY == p1:
            return p2
        if EllipticCurve.IDENTITY == p2:
            return p1

        if p1 == p2:
            if p1[1] == 0:
                return EllipticCurve.IDENTITY

            s = ((3 * p1[0] * p1[0] + self.a) * num.inverse(2 * p1[1], self.p)) % self.p
        else:
            if p2[0] - p1[0] % self.p == 0:
                return EllipticCurve.IDENTITY

            s = ((p2[1] - p1[1]) * num.inverse(p2[0] - p1[0], self.p)) % self.p

        x3 = ((s * s) - p1[0] - p2[0]) % self.p
        y3 = (s * (p1[0] - x3) - p1[1]) % self.p

        return (x3, y3)

    """
    Computes the addition of p with itself n times

    multiply: n, pt (x,y) -> pt (x,y)
    """
    def multiply(self, n, p):
        r = EllipticCurve.IDENTITY

        for i in bin(n)[2:][::-1]: # Reverses the bits of n
            if i == "1":
                r = self._add(r,p)

            p = self._add(p,p)

        return r

    """
    Determines if pt is an element in the group

    is_element: pt (x,y) -> bool
    """
    def is_element(self, pt):
        return pt == EllipticCurve.IDENTITY or ((pt[1] ** 2) % self.p) == ((((pt[0] ** 3) % self.p) + ((self.a * pt[0]) % self.p) + self.b) % self.p)
