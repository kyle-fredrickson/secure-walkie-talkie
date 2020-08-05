import hashlib

def sha3_256(b):
    return hashlib.sha3_256(b).digest()

def sha3_512(b):
    return hashlib.sha3_512(b).digest()

def sha3_512_split(b):
    hash = sha3_512(b)
    x = hash[:len(hash) // 2]
    y = hash[len(hash) // 2:]
    return (x,y)

def main():
    print(sha3_256(b"hi"))


"""
class SHA3_256:
    r = 1088
    c = 512

    l = 6
    w = 2 ** l
    rounds = 12 + (2 * l)
    size = 5 * 5 * w

    ### Utilities ###

    def get_state(state):
        #a = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
        a = np.zeros((5,5,w), dtype = int)

        for x in range(5):
            for y in range(5):
                lane_xy = read_state(x,y,state)
                for z in range(w):
                    a[x][y][z] = get_z(z, lane_xy)

        return a

    ### Processing ###

    def pad10_1(r, m):
        j = (-len(m) - 2) % r
        return '1' + '0'*j + '1'

    ### SHA3-256 ###

    def hash(m):
        return SHA3_256.r

    def keccak(a):
        pass

    def round(a,i):
        a = theta(a)
        a = rho(a)
        a = pi(a)
        a = chi(a)
        a = iota(a,i)

        return a

    def theta(a):
        a1 = list3d(5,5,w)#np.zeros((5,5,w), dtype = int)
        c = list2d(5,w)
        d = list2d(5,w)

        for x in range(5):
            for z in range(w):
                c[x][z] = get_column(x,z,a)

        for x in range(5):
            for z in range(w):
                d[x][z] = c[(x-1)%5][z] ^ c[(x+1)%5][(z-1)%w]

        for x in range(5):
            for y in range(5):
                for z in range(w):
                    a1[x][y][z] = a[x][y][z] ^ d[x][z]

        return a1

    def rho(a):
        a1 = list3d(5,5,w)

        for z in range(w):
            a1[0][0][z] = a[0][0][z]

        (x,y) = (1,0)

        for t in range(24):
            for z in range(w):
                z1 = (z - int(((t+1) * (t+2)) / 2)) % w
                a1[x][y][z] = a[x][y][z1]
            (x1,y1) = (y, (2*x + 3*y) % 5 )
            (x,y) = (x1,y1)

        return a1

    def pi(a):
        a1 = list3d(5,5,w)

        for x in range(5):
            for y in range(5):
                for z in range(w):
                    a1[x][y][z] = a[(x + 3*y) % 5][x][z]

        return a1

    def chi(a):
        a1 = list3d(5,5,w)

        for x in range(5):
            for y in range(5):
                for z in range(w):
                    a1[x][y][z] = a[x][y][z] ^ ((a[(x + 1) % 5][y][z] ^ 1) & a[(x + 2) % 5][y][z])
        return a1

    def iota(a,i):
        a1 = a.copy()

        RC = 0x0

        for j in range(l + 1):
            RC = RC | (rc(j + (7 * i)) << ((2 ** j) -1))

        for z in range(w):
            a1[0][0][z] = a1[0][0][z] ^ get_z(z, RC)

        return a1

    def rc(t):
        if (t % 255) == 0:
            return 1
        r = 1

        for i in range(t % 255):
            r = r << 1
            if r & 0x100:
                r = r ^ 0x71

        return r & 0x1
"""

if __name__ == "__main__":
    main()
