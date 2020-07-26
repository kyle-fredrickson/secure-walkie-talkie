import json
import sys

sys.path.append("../../python/src")
import UtilityTransforms as ut

def test_bint_to_b64(tests):
    for test in tests:
        if not (ut.bint_to_b64_string(test["input"]) == test["output"] and ut.b64_string_to_bint(test["output"]) == test["input"]):
            return False

    return True

def test_ascii_to_integer(tests):
    for test in tests:
        if not (ut.ascii_to_bint(test["input"]) == test["output"] and ut.bint_to_ascii(test["output"]) == test["input"]):
            return False

    return True

def test_bytes_to_integer(tests):
    for test in tests:
        if not (ut.bytes_to_bint(test["input"].encode()) == test["output"] and ut.bint_to_bytes(test["output"]) == test["input"].encode()):
            return False

    return True

def test(js):
    for (key, value) in js.items():
        if key == "big_int_to_b64_string":
            if not test_bint_to_b64(value):
                return False
        elif key == "ascii_to_integer":
            if not test_ascii_to_integer(value):
                return False
        elif key == "bytes_to_integer":
            if not test_bytes_to_integer(value):
                return False
        else:
            return False

    return True



def main():
    with open("../test_vectors.json") as file:
        js = json.load(file)

    passed = test(js)

    try:
        assert(passed)
        print("Test passed.")
    except:
        print("Test failed.")


if __name__ == "__main__":
    main()