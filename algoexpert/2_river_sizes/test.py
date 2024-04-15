import river
import unittest


class TestProgram(unittest.TestCase):
    def test_complex_map(self):
        testInput = [
            [1, 0, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 1, 1, 0],
        ]
        expected = [1, 2, 2, 2, 5]
        self.assertEqual(sorted(river.riverSizes(testInput)), expected)

    def test_one_river(self):
        testInput = [
            [1],
        ]
        expected = [1]
        self.assertEqual(sorted(river.riverSizes(testInput)), expected)

    def test_case_one_land(self):
        testInput = [
            [0],
        ]
        expected = []
        self.assertEqual(sorted(river.riverSizes(testInput)), expected)
