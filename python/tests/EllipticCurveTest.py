import sys

sys.path.append('../src/')
from EllipticCurve import EllipticCurve

def main():
    E = EllipticCurve(2,2,17)

    ### is_element test ###
    element_test = (E.is_element((5,1)) and not E.is_element((0,5)))
    print("is_element (passed):", element_test)

    ### _add test ###
    identity_test = E._add(EllipticCurve.IDENTITY, EllipticCurve.IDENTITY) == EllipticCurve.IDENTITY
    add_test = E._add((9,16),(5,1)) == (16,13)
    print("_add (passed):", identity_test and add_test)

    ### multiply test ###
    multiply_test = True
    for i in range(1, 20):
        m = E.multiply(i, (5,1))
        multiply_test = multiply_test and (i == 19 or m != EllipticCurve.IDENTITY) and (i != 19 or m == EllipticCurve.IDENTITY)

    print("multiply (passed):", multiply_test)

if __name__ == "__main__":
    main()
