from os import listdir, getcwd
import core.common as c

def lsplit(target: list, value):
    idx_list = [idx for idx, val in enumerate(target) if val==value]
    res = [target[i: j] for i, j in zip([0] + idx_list, idx_list +([len(target)] if idx_list[-1] != len(target) else []))]
    res = [list(filter(lambda x:x!=value, y)) for y in res]
    return res
tests = listdir(getcwd() + "/tests/")

for test in tests:
    testfile = open(getcwd() + "/tests/" + test, "r", encoding="utf-8")
    testlines = testfile.readlines()
    code, y = lsplit(testlines, "END TEST CODE\n")
    tests, results = lsplit(y, "END TEST DATA\n")

    code = "".join(code)
    tests = ["".join(x) for x in tests]
    tests = "".join(tests)
    tests = tests.split("DELIM")

    results = ["".join(x).replace("\n","") for x in results]
    results = list(filter(lambda x: x != "DELIM", results))

    global c, loc
    loc = {"out":None}
    test_expr = lambda x:exec(code.replace("PARAM", x), globals(), loc)

    for index, each in enumerate(tests):
        print(f"==== test {index:2} ====")
        print(each)
        test_expr(each)
        print(loc['out'])
        print(results[index])
        if str(loc["out"]) != str(results[index]):
            print("FAIL")
        else:
            print("PASS")
