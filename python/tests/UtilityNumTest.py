import sys

sys.path.append('../src/')
import UtilityNum as num

def main():
    ### generate_prime test ###
    bit_len = 100
    p = num.generate_prime(bit_len)
    print("generate_prime (passed):", num.miller_rabin(p) and len(bin(p)[2:]) == bit_len)
    print("p =", p)

    ### miller_rabin test ###
    print("miller_rabin (passed):", num.miller_rabin(23568610299853083732433874969014771975888202419342692705717508036659889667059423136455086558447072526411177111354243292780596293358164300298518819344484371759638338211203662869097829185323881832019018069232259133301555540281391106315692456929231529470093933032042620316436660858420452555402629809071980239122671081292794460959022604403825229283946083002045535713766021026197551861927623152173713733155402539462799575273740291586435562669214677603756105478487057278946734913565210432537940206201260517136686811323805238690229141586287974318033015838546230823577334111072644224729724126340220743318562455432854907501031)) # fails for whatever reason

    ### inverse test ###
    q = 2 ** 16 + 1
    inverse_exists_test = q * num.inverse(q, p) % p == 1

    try:
        num.inverse(2,4)
        inverse_not_exist_test = False
    except:
        inverse_not_exist_test = True

    print("inverse (passed):", inverse_exists_test and inverse_not_exist_test)

    ### gcd test ###
    q = num.generate_prime(bit_len)
    r = num.generate_prime(bit_len)
    if p * q < q * r:
        a = q * r
        b = p * q
    else:
        a = p * q
        b = q * r

    gcd_test = num.gcd(a,b) == q

    print("gcd (passed):", gcd_test)

    ### extended_euclidean_algoritm test ###
    (gcd, t, s) = num.extended_euclidian_algorithm(a,b)
    eea_test = (((a * s) + (b * t)) % a) == (gcd % a)
    print("extended_extended_euclidian_algorithm (passed):", eea_test)

if __name__ == "__main__":
    main()


"""
"""
