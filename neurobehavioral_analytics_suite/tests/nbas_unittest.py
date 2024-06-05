import unittest


def loadTest(test):
    test = unittest.TestLoader().loadTestsFromTestCase(test)
    all_tests.append(test)


if __name__ == '__main__':
    all_tests = list()
    # Load test sets
    # loadTest()

    # Run the tests
    for test_set in all_tests:
        unittest.TextTestRunner(verbosity=1).run(test_set)
