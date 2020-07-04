import sys

sys.path.append('../src/')
from UtilityConfig import UtilityConfig
import UtilityNum as num
import DHKE as d

def main():
    uc = UtilityConfig("../config/test.json")
    dhke1 = d.DHKE(uc.dh_p, uc.dh_g)
    dhke2 = d.DHKE(uc.dh_p, uc.dh_g)
    print("DHKE Constructor passed:", dhke1 != None and dhke2 != None)

    ss1 = dhke1.get_shared_secret(dhke2.X)
    ss2 = dhke2.get_shared_secret(dhke1.X)
    print("Key Exchange passed:", ss1 == ss2)

if __name__ == "__main__":
    main()
